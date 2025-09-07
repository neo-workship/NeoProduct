/**
 * Weather functionality for block_blockdemo
 *
 * @module     block_blockdemo/weather
 * @copyright  2025 Your Name <your@email.com>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

import Ajax from "core/ajax";
import Notification from "core/notification";
import Templates from "core/templates";
import { get_string as getString } from "core/str";
import $ from "jquery";
import Log from "core/log";

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
      ...config,
    };

    this.isLoading = false;
    this.cache = new Map();

    // Bind methods to maintain context
    this.handleGetWeather = this.handleGetWeather.bind(this);
    this.handleRefreshWeather = this.handleRefreshWeather.bind(this);
    this.handleCityChange = this.handleCityChange.bind(this);
  }

  /**
   * Initialize the weather functionality
   */
  init() {
    Log.debug("Initializing weather module", "block_blockdemo");

    // Attach event listeners
    this.attachEventListeners();

    // Load initial weather data if auto-load is enabled
    if (this.config.autoLoad) {
      this.loadWeatherData(this.config.defaultCityCode, false);
    }

    Log.debug("Weather module initialized successfully", "block_blockdemo");
  }

  /**
   * Attach event listeners to DOM elements
   */
  attachEventListeners() {
    const $container = $(SELECTORS.BLOCK_CONTAINER);

    // Get weather button click
    $container.on("click", SELECTORS.WEATHER_BUTTON, this.handleGetWeather);

    // Refresh weather button click
    $container.on("click", SELECTORS.REFRESH_BUTTON, this.handleRefreshWeather);

    // City selection change
    $container.on("change", SELECTORS.CITY_SELECT, this.handleCityChange);

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

    await this.loadWeatherData(cityCode, true);
  }

  /**
   * Handle city selection change
   * @param {Event} e Change event
   */
  async handleCityChange(e) {
    const cityCode = $(e.currentTarget).val();
    if (cityCode) {
      await this.loadWeatherData(cityCode, false);
    }
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
          await this.displayWeatherData(cachedData.data);
          this.isLoading = false;
          return;
        }
      }

      // Show loading state
      await this.showLoadingState();

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

      // Cache the response
      this.cache.set(cityCode, {
        data: response,
        timestamp: Date.now(),
      });

      // Display the weather data
      await this.displayWeatherData(response);

      // Show success notification
      const successMessage = await getString(
        "weather_loaded_successfully",
        "block_blockdemo"
      );
      Notification.addNotification({
        message: successMessage,
        type: "success",
      });

      Log.debug("天气资料已成功载入", "block_blockdemo", response);
    } catch (error) {
      Log.error("加载天气数据失败", "block_blockdemo", error);
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
    if (!weatherData.success || !weatherData.data) {
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

      // Render the template
      const html = await Templates.render(
        "block_blockdemo/weather_display",
        templateContext
      );

      // Update the container with animation
      $container.fadeOut(200, function () {
        $(this).html(html).fadeIn(300);
      });

      Log.debug("Weather data displayed successfully", "block_blockdemo");
    } catch (error) {
      Log.error("Failed to render weather template", "block_blockdemo", error);
      throw error;
    }
  }

  /**
   * Show loading state
   */
  async showLoadingState() {
    const $loadingContainer = $(SELECTORS.WEATHER_LOADING);
    const $button = $(SELECTORS.WEATHER_BUTTON);

    if ($loadingContainer.length > 0) {
      $loadingContainer.show();
    }

    if ($button.length > 0) {
      const loadingText = await getString("loading", "block_blockdemo");
      $button
        .prop("disabled", true)
        .data("original-text", $button.text())
        .text(loadingText);
    }
  }

  /**
   * Hide loading state
   */
  async hideLoadingState() {
    const $loadingContainer = $(SELECTORS.WEATHER_LOADING);
    const $button = $(SELECTORS.WEATHER_BUTTON);

    if ($loadingContainer.length > 0) {
      $loadingContainer.hide();
    }

    if ($button.length > 0) {
      const originalText = $button.data("original-text");
      if (originalText) {
        $button.prop("disabled", false).text(originalText);
      }
    }
  }

  /**
   * Handle errors
   * @param {Error} error The error object
   */
  async handleError(error) {
    Log.error("Weather module error", "block_blockdemo", error);

    // Determine error message
    let errorMessage;
    if (error.message) {
      errorMessage = error.message;
    } else {
      errorMessage = await getString(
        "weather_error_generic",
        "block_blockdemo"
      );
    }

    // Show error notification
    Notification.addNotification({
      message: errorMessage,
      type: "error",
    });

    // Show error in container if it exists
    const $container = $(SELECTORS.WEATHER_CONTAINER);
    if ($container.length > 0) {
      const errorHtml = await Templates.render(
        "block_blockdemo/weather_error",
        {
          message: errorMessage,
        }
      );
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
   * @param {string} cityCode Optional city code to clear, if not provided clears all
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
   * Get current cache size
   * @return {number} Number of cached entries
   */
  getCacheSize() {
    return this.cache.size;
  }
}

// Module instance storage
let moduleInstance = null;

/**
 * Initialize the weather module
 * @param {Object} config Configuration object
 */
export const init = (config = {}) => {
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
};

/**
 * Get the current module instance
 * @return {WeatherModule|null} Current module instance
 */
export const getInstance = () => {
  return moduleInstance;
};

/**
 * Destroy the module instance
 */
export const destroy = () => {
  if (moduleInstance) {
    // Remove event listeners
    $(SELECTORS.BLOCK_CONTAINER).off("click", SELECTORS.WEATHER_BUTTON);
    $(SELECTORS.BLOCK_CONTAINER).off("click", SELECTORS.REFRESH_BUTTON);
    $(SELECTORS.BLOCK_CONTAINER).off("change", SELECTORS.CITY_SELECT);

    moduleInstance = null;
    Log.debug("Weather module destroyed", "block_blockdemo");
  }
};
