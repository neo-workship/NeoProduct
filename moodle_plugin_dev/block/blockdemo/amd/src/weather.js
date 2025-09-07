/**
 * Weather functionality for block_blockdemo
 *
 * @module     block_blockdemo/weather
 * @copyright  2025 Your Name <your@email.com>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

// 修复：正确的AMD模块定义
define([
  "core/ajax",
  "core/notification",
  "core/templates",
  "core/str",
  "jquery",
  "core/log",
], function (Ajax, Notification, Templates, Str, $, Log) {
  /**
   * Selectors for weather functionality
   */
  const SELECTORS = {
    WEATHER_BUTTON: '[data-action="get-weather"]',
    WEATHER_CONTAINER: '[data-region="weather-display"]',
    WEATHER_LOADING: '[data-region="weather-loading"]',
    REFRESH_BUTTON: '[data-action="refresh-weather"]',
    CITY_SELECT: '[data-field="city-code"]',
    BLOCK_CONTAINER: ".block_blockdemo",
  };

  /**
   * Weather module class
   */
  class WeatherModule {
    /**
     * Constructor
     * @param {Object} config Configuration object
     */
    constructor(config = {}) {
      this.config = {
        defaultCityCode: "110101",
        blockInstanceId: null,
        hasApiKey: false,
        autoLoad: false,
        ...config,
      };

      this.isLoading = false;
      this.cache = new Map();
      this.stringCache = new Map();

      // Bind methods to maintain context
      this.handleGetWeather = this.handleGetWeather.bind(this);
      this.handleRefreshWeather = this.handleRefreshWeather.bind(this);
    }

    /**
     * Initialize the weather functionality
     */
    async init() {
      Log.debug("Initializing weather module", "block_blockdemo", this.config);

      // 预加载字符串
      await this.preloadStrings();

      // 检查API密钥
      if (!this.config.hasApiKey) {
        Log.warn("Weather API key not configured", "block_blockdemo");
        await this.showApiKeyMissingMessage();
        return;
      }

      // Attach event listeners
      this.attachEventListeners();

      // Load initial weather data if auto-load is enabled
      if (this.config.autoLoad) {
        await this.loadWeatherData(this.config.defaultCityCode, false);
      }

      Log.debug("Weather module initialized successfully", "block_blockdemo");
    }

    /**
     * 预加载需要的字符串
     */
    async preloadStrings() {
      try {
        const strings = [
          { key: "loading", component: "block_blockdemo" },
          { key: "loading_weather", component: "block_blockdemo" },
          { key: "weather_loaded_successfully", component: "block_blockdemo" },
          { key: "weather_error_generic", component: "block_blockdemo" },
          { key: "weather_api_key_missing", component: "block_blockdemo" },
        ];

        const results = await Str.get_strings(strings);

        // 缓存字符串
        strings.forEach((str, index) => {
          this.stringCache.set(str.key, results[index]);
        });

        Log.debug("Strings preloaded", "block_blockdemo", this.stringCache);
      } catch (error) {
        Log.error("Failed to preload strings", "block_blockdemo", error);
      }
    }

    /**
     * 获取缓存的字符串
     * @param {string} key 字符串键
     * @returns {string} 字符串值
     */
    getString(key) {
      return this.stringCache.get(key) || key;
    }

    /**
     * 显示API密钥缺失的消息
     */
    async showApiKeyMissingMessage() {
      const $container = $(SELECTORS.WEATHER_CONTAINER);
      if ($container.length > 0) {
        const message = this.getString("weather_api_key_missing");
        const html = `
                    <div class="alert alert-warning">
                        <i class="fa fa-exclamation-triangle"></i>
                        ${message}
                    </div>
                `;
        $container.html(html);
      }
    }

    /**
     * Attach event listeners to DOM elements
     */
    attachEventListeners() {
      const $container = $(SELECTORS.BLOCK_CONTAINER);

      // 移除现有事件监听器避免重复绑定
      $container.off("click.weather");

      // Get weather button click
      $container.on(
        "click.weather",
        SELECTORS.WEATHER_BUTTON,
        this.handleGetWeather
      );

      // Refresh weather button click
      $container.on(
        "click.weather",
        SELECTORS.REFRESH_BUTTON,
        this.handleRefreshWeather
      );

      Log.debug("Event listeners attached", "block_blockdemo");
    }

    /**
     * Handle get weather button click
     * @param {Event} e Click event
     */
    async handleGetWeather(e) {
      e.preventDefault();

      const $button = $(e.currentTarget);
      const cityCode = $button.data("city-code") || this.config.defaultCityCode;

      Log.debug("Get weather button clicked", "block_blockdemo", { cityCode });

      await this.loadWeatherData(cityCode, false);
    }

    /**
     * Handle refresh weather button click
     * @param {Event} e Click event
     */
    async handleRefreshWeather(e) {
      e.preventDefault();

      const $button = $(e.currentTarget);
      const cityCode = $button.data("city-code") || this.config.defaultCityCode;

      Log.debug("Refresh weather button clicked", "block_blockdemo", {
        cityCode,
      });

      await this.loadWeatherData(cityCode, true);
    }

    /**
     * Load weather data from the server
     * @param {string} cityCode City code to get weather for
     * @param {boolean} refresh Whether to force refresh cache
     */
    async loadWeatherData(cityCode, refresh = false) {
      if (this.isLoading) {
        Log.debug("Weather request already in progress", "block_blockdemo");
        return;
      }

      this.isLoading = true;

      try {
        // Check local cache first (unless refresh is requested)
        if (!refresh && this.cache.has(cityCode)) {
          const cachedData = this.cache.get(cityCode);
          const now = Date.now();

          // Use cache if less than 5 minutes old
          if (now - cachedData.timestamp < 300000) {
            Log.debug("Using cached weather data", "block_blockdemo");
            await this.displayWeatherData(cachedData.data);
            return;
          }
        }

        // Show loading state
        await this.showLoadingState();

        Log.debug("Calling weather API", "block_blockdemo", {
          cityCode,
          refresh,
        });

        // Call the web service
        const response = await Ajax.call([
          {
            methodname: "block_blockdemo_get_weather",
            args: {
              citycode: cityCode,
              refresh: refresh,
            },
          },
        ])[0];

        Log.debug("Weather API response received", "block_blockdemo", response);

        // Cache the response
        this.cache.set(cityCode, {
          data: response,
          timestamp: Date.now(),
        });

        // Display the weather data
        await this.displayWeatherData(response);

        // Show success notification
        const successMessage = this.getString("weather_loaded_successfully");
        if (successMessage) {
          Notification.addNotification({
            message: successMessage,
            type: "success",
          });
        }
      } catch (error) {
        Log.error("Failed to load weather data", "block_blockdemo", error);
        await this.handleError(error);
      } finally {
        this.isLoading = false;
        await this.hideLoadingState();
      }
    }

    /**
     * Display weather data in the UI
     * @param {Object} weatherData Weather data from the server
     */
    async displayWeatherData(weatherData) {
      if (!weatherData || !weatherData.success || !weatherData.data) {
        throw new Error("Invalid weather data received");
      }

      const $container = $(SELECTORS.WEATHER_CONTAINER);
      if ($container.length === 0) {
        Log.warn("Weather container not found", "block_blockdemo");
        return;
      }

      try {
        // Prepare template context
        const templateContext = {
          ...weatherData.data,
          hasTemperature: weatherData.data.temperature !== null,
          hasHumidity: weatherData.data.humidity !== null,
          hasWind: weatherData.data.winddirection && weatherData.data.windpower,
          formattedTime: this.formatDateTime(weatherData.data.reporttime),
          temperatureDisplay: this.formatTemperature(
            weatherData.data.temperature
          ),
          humidityDisplay: this.formatHumidity(weatherData.data.humidity),
        };

        Log.debug(
          "Rendering weather template",
          "block_blockdemo",
          templateContext
        );

        // 简化版显示，不依赖模板
        const html = this.generateWeatherHtml(templateContext);

        // Update the container with animation
        $container.fadeOut(200, function () {
          $(this).html(html).fadeIn(300);
        });

        Log.debug("Weather data displayed successfully", "block_blockdemo");
      } catch (error) {
        Log.error("Failed to display weather data", "block_blockdemo", error);
        throw error;
      }
    }

    /**
     * 生成天气显示的HTML
     * @param {Object} data 天气数据
     * @returns {string} HTML字符串
     */
    generateWeatherHtml(data) {
      return `
                <div class="weather-data">
                    <div class="weather-location">
                        <strong>${data.province} ${data.city}</strong>
                    </div>
                    <div class="weather-info">
                        <div class="weather-item">
                            <div class="weather-label">天气</div>
                            <div class="weather-value">${data.weather}</div>
                        </div>
                        ${
                          data.hasTemperature
                            ? `
                        <div class="weather-item">
                            <div class="weather-label">温度</div>
                            <div class="weather-value weather-temperature">${data.temperatureDisplay}</div>
                        </div>
                        `
                            : ""
                        }
                        ${
                          data.hasHumidity
                            ? `
                        <div class="weather-item">
                            <div class="weather-label">湿度</div>
                            <div class="weather-value weather-humidity">${data.humidityDisplay}</div>
                        </div>
                        `
                            : ""
                        }
                        ${
                          data.hasWind
                            ? `
                        <div class="weather-item">
                            <div class="weather-label">风向</div>
                            <div class="weather-value weather-wind">${data.winddirection} ${data.windpower}级</div>
                        </div>
                        `
                            : ""
                        }
                    </div>
                    <div class="weather-time">
                        更新时间: ${data.formattedTime}
                    </div>
                </div>
            `;
    }

    /**
     * Show loading state
     */
    async showLoadingState() {
      const $loadingContainer = $(SELECTORS.WEATHER_LOADING);
      const $buttons = $(
        SELECTORS.WEATHER_BUTTON + ", " + SELECTORS.REFRESH_BUTTON
      );

      if ($loadingContainer.length > 0) {
        $loadingContainer.show();
      }

      if ($buttons.length > 0) {
        const loadingText = this.getString("loading");
        $buttons.each(function () {
          const $btn = $(this);
          $btn
            .prop("disabled", true)
            .data("original-text", $btn.text())
            .text(loadingText);
        });
      }
    }

    /**
     * Hide loading state
     */
    async hideLoadingState() {
      const $loadingContainer = $(SELECTORS.WEATHER_LOADING);
      const $buttons = $(
        SELECTORS.WEATHER_BUTTON + ", " + SELECTORS.REFRESH_BUTTON
      );

      if ($loadingContainer.length > 0) {
        $loadingContainer.hide();
      }

      if ($buttons.length > 0) {
        $buttons.each(function () {
          const $btn = $(this);
          const originalText = $btn.data("original-text");
          if (originalText) {
            $btn.prop("disabled", false).text(originalText);
          }
        });
      }
    }

    /**
     * Handle errors
     * @param {Error} error The error object
     */
    async handleError(error) {
      Log.error("Weather module error", "block_blockdemo", error);

      // Determine error message
      let errorMessage =
        error.message || this.getString("weather_error_generic");

      // Show error notification
      Notification.addNotification({
        message: errorMessage,
        type: "error",
      });

      // Show error in container if it exists
      const $container = $(SELECTORS.WEATHER_CONTAINER);
      if ($container.length > 0) {
        const errorHtml = `
                    <div class="weather-error alert alert-danger">
                        <i class="fa fa-exclamation-circle"></i>
                        ${errorMessage}
                    </div>
                `;
        $container.html(errorHtml);
      }
    }

    /**
     * Format temperature for display
     * @param {number} temperature Temperature value
     * @return {string} Formatted temperature
     */
    formatTemperature(temperature) {
      if (temperature === null || temperature === undefined) {
        return "--";
      }
      return `${temperature}°C`;
    }

    /**
     * Format humidity for display
     * @param {number} humidity Humidity value
     * @return {string} Formatted humidity
     */
    formatHumidity(humidity) {
      if (humidity === null || humidity === undefined) {
        return "--";
      }
      return `${humidity}%`;
    }

    /**
     * Format date time for display
     * @param {string} datetime DateTime string
     * @return {string} Formatted datetime
     */
    formatDateTime(datetime) {
      try {
        const date = new Date(datetime);
        return date.toLocaleString();
      } catch (e) {
        return datetime;
      }
    }

    /**
     * Clear cache for specific city or all cities
     * @param {string} cityCode Optional city code to clear
     */
    clearCache(cityCode = null) {
      if (cityCode) {
        this.cache.delete(cityCode);
      } else {
        this.cache.clear();
      }
      Log.debug("Weather cache cleared", "block_blockdemo", { cityCode });
    }

    /**
     * Destroy the module instance
     */
    destroy() {
      // Remove event listeners
      $(SELECTORS.BLOCK_CONTAINER).off("click.weather");

      // Clear caches
      this.clearCache();
      this.stringCache.clear();

      Log.debug("Weather module destroyed", "block_blockdemo");
    }
  }

  // Module instance storage
  let moduleInstance = null;

  return {
    /**
     * Initialize the weather module
     * @param {Object} config Configuration object
     */
    init: function (config = {}) {
      Log.debug("Weather module init called", "block_blockdemo", config);

      // Ensure we only have one instance per page
      if (moduleInstance) {
        Log.debug("Weather module already initialized", "block_blockdemo");
        return moduleInstance;
      }

      // Create and initialize new instance
      moduleInstance = new WeatherModule(config);
      moduleInstance.init();

      return moduleInstance;
    },

    /**
     * Get the current module instance
     * @return {WeatherModule|null} Current module instance
     */
    getInstance: function () {
      return moduleInstance;
    },

    /**
     * Destroy the module instance
     */
    destroy: function () {
      if (moduleInstance) {
        moduleInstance.destroy();
        moduleInstance = null;
      }
    },
  };
});
