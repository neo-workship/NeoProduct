// 图表组件相关的JavaScript功能

/**
 * 图表工具类
 */
class ChartUtils {
  /**
   * 生成随机颜色
   * @param {number} count 颜色数量
   * @returns {string[]} 颜色数组
   */
  static generateColors(count) {
    const colors = [
      "#3b82f6",
      "#10b981",
      "#f59e0b",
      "#ef4444",
      "#8b5cf6",
      "#06b6d4",
      "#84cc16",
      "#f97316",
      "#ec4899",
      "#6366f1",
    ];

    if (count <= colors.length) {
      return colors.slice(0, count);
    }

    // 如果需要更多颜色，生成随机颜色
    const result = [...colors];
    for (let i = colors.length; i < count; i++) {
      result.push(this.generateRandomColor());
    }
    return result;
  }

  /**
   * 生成随机颜色
   * @returns {string} 十六进制颜色值
   */
  static generateRandomColor() {
    return "#" + Math.floor(Math.random() * 16777215).toString(16);
  }

  /**
   * 格式化数据用于图表显示
   * @param {Array} data 原始数据
   * @param {string} labelKey 标签字段名
   * @param {string} valueKey 值字段名
   * @returns {Object} 格式化后的数据
   */
  static formatChartData(data, labelKey = "label", valueKey = "value") {
    return {
      labels: data.map((item) => item[labelKey]),
      values: data.map((item) => item[valueKey]),
      colors: this.generateColors(data.length),
    };
  }

  /**
   * 创建仪表盘数据
   * @param {number} current 当前值
   * @param {number} target 目标值
   * @param {string} unit 单位
   * @returns {Object} 仪表盘数据
   */
  static createGaugeData(current, target, unit = "") {
    const percentage = Math.round((current / target) * 100);
    const color =
      percentage >= 80 ? "#10b981" : percentage >= 60 ? "#f59e0b" : "#ef4444";

    return {
      current,
      target,
      percentage,
      unit,
      color,
      status:
        percentage >= 80
          ? "excellent"
          : percentage >= 60
          ? "good"
          : "needs-improvement",
    };
  }
}

/**
 * 图表动画工具
 */
class ChartAnimations {
  /**
   * 数字计数动画
   * @param {HTMLElement} element 目标元素
   * @param {number} endValue 结束值
   * @param {number} duration 动画时长（毫秒）
   */
  static animateNumber(element, endValue, duration = 1000) {
    const startValue = 0;
    const startTime = performance.now();

    function updateNumber(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // 使用缓动函数
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const currentValue = Math.round(
        startValue + (endValue - startValue) * easeOutQuart
      );

      element.textContent = currentValue.toLocaleString();

      if (progress < 1) {
        requestAnimationFrame(updateNumber);
      }
    }

    requestAnimationFrame(updateNumber);
  }

  /**
   * 进度条动画
   * @param {HTMLElement} element 进度条元素
   * @param {number} percentage 目标百分比
   * @param {number} duration 动画时长
   */
  static animateProgressBar(element, percentage, duration = 1000) {
    const startTime = performance.now();

    function updateProgress(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      const currentPercentage = percentage * progress;
      element.style.width = `${currentPercentage}%`;

      if (progress < 1) {
        requestAnimationFrame(updateProgress);
      }
    }

    requestAnimationFrame(updateProgress);
  }
}

// 示例数据生成器
class ChartDataGenerator {
  /**
   * 生成销售数据
   * @param {number} months 月份数量
   * @returns {Array} 销售数据
   */
  static generateSalesData(months = 12) {
    const data = [];
    const monthNames = [
      "1月",
      "2月",
      "3月",
      "4月",
      "5月",
      "6月",
      "7月",
      "8月",
      "9月",
      "10月",
      "11月",
      "12月",
    ];

    for (let i = 0; i < months; i++) {
      data.push({
        month: monthNames[i],
        sales: Math.floor(Math.random() * 100000) + 50000,
        profit: Math.floor(Math.random() * 30000) + 10000,
      });
    }

    return data;
  }

  /**
   * 生成用户活跃度数据
   * @param {number} days 天数
   * @returns {Array} 用户活跃度数据
   */
  static generateUserActivityData(days = 30) {
    const data = [];
    const now = new Date();

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);

      data.push({
        date: date.toISOString().split("T")[0],
        activeUsers: Math.floor(Math.random() * 5000) + 1000,
        newUsers: Math.floor(Math.random() * 500) + 50,
      });
    }

    return data;
  }
}

// 导出到全局作用域
if (typeof window !== "undefined") {
  window.ChartUtils = ChartUtils;
  window.ChartAnimations = ChartAnimations;
  window.ChartDataGenerator = ChartDataGenerator;
}
