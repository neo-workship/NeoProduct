// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * TODO describe module settings
 *
 * @module     block_neo_chat/settings
 * @copyright  2025 YOUR NAME <your@email.com>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

/**
 * 初始化设置表单事件监听
 *
 * 当聊天类型选择框值变化时：
 * 1. 为表单添加样式类
 * 2. 禁用表单
 * 3. 自动提交表单
 *
 * @exports
 */

export const init = () => {
  document
    .querySelector("#id_s_block_neo_chat_type") // 用于选择具有特定 ID (id_s_block_neo_chat_type) 的 HTML 元素
    ?.addEventListener("change", (e) => {
      /**
       * 初始化设置表单的变更事件监听器
       * 当id_s_block_neo_chat_type元素的值发生变化时：
       * 1. 为settingsform添加block_neo_chat和disabled类
       * 2. 自动触发表单提交按钮的点击事件
       */
      document.querySelector(".settingsform").classList.add("block_neo_chat");
      document.querySelector(".settingsform").classList.add("disabled");
      document.querySelector('.settingsform button[type="submit"]').click();
    });

  document.querySelector(`.`);
};
