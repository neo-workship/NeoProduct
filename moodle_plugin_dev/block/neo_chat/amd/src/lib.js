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
 * TODO describe module lib
 *
 * @module     block_neo_chat/lib
 * @copyright  2025 YOUR NAME <your@email.com>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

var questionString = "输入问题......";
var errorString = "错误,请稍候再试......";

export const init = (data) => {
  const blockId = data["blockId"];
  const api_type = data["api_type"];
  const persistConvo = data["persistConvo"];

  window.addEventListener(
    "resize",
    (event) => {
      event.stopImmediatePropagation();
    },
    true
  );

  document
    .querySelector(
      `.block_neo_chat[data-instance-id]=${blockId} #neochat_input`
    ).addEventListener("keyup", (e) => {
      if (e.which === 13 && e.target.value !== "") {
        addToChatLog('用户',e.target.value,blockId);
        createCompletion();
        e.target.value = "";
      }
    });
};


/**
 * 向聊天日志中添加一条消息
 * 
 * @function addToChatLog
 * @param {string} type - 消息类型，可以是多个类名用空格分隔
 * @param {string} message - 要显示的文本消息内容
 * @param {string} blockId - 聊天块实例ID，用于定位DOM元素
 * @description 创建消息元素并添加到指定聊天容器中，自动调整宽度和滚动位置
 */
const addToChatLog = (type, message, blockId) => {
  let messageContainer = document.querySelector(
    `.block_openai_chat[data-instance-id='#${blockId}'] #neochat_log`
  );

  const messageElem = document.createElement("div");
  
  messageElem.classList.add("neochat_message");

  for (let className of type.split(" ")) {
    messageElem.classList.add(className);
  }

  const messageText = document.createElement("span");
  messageText.innerText = message;
  messageElem.append(messageText);

  messageContainer.append(messageElem);
  if (messageText.OffsetWidth) {
    messageElem.style.width = messageText.offsetWidth + 40 + "px";
  }

  messageContainer.scrollTop = messageContainer.scrollHeight;
  messageContainer.closest(".block_neo_chat > div").scrollTop =
    messageContainer.scrollHeight;
};


const createCompletion = (message,blockId,api_type) => {
  let threadId = null
  let chatData
  const history = buildTranscript(blockId)

  document.querySelector(`.block_neo_chat[data-instance-id='${blockId}'] #control_bar`).classList.add('disabled')
  document.querySelector(`.block_neo_chat[data-instance-id='${blockId}'] #neochat_input`).classList.remove('error')
  document.querySelector(`.block_neo_chat[data-instance-id='${blockId}'] #neochat_input`).placeholder= questionString
  document.querySelector(`.block_neo_chat[data-instance-id='${blockId}'] #neochat-input`).blur()
  addToChatLog('AI助手','正在处理......',blockId)

  fetch(`${M.cfg.wwwroot}/blocks/neo_chat/api/completion.php`,{
    method: 'POST',
    body:JSON.stringify({
      message: message,
      history: history,
      blockId: blockId,
      threadId: threadId
    })
  }).then(response=>{
    let messageContainer = document.querySelector(`.block_openai_chat[data-instance-id='${blockId}'] #neochat_log`)
    messageContainer.removeChild(messageContainer.lastElementChild)
    document.querySelector(`.block_neo_chat[data-instance-id]=${blockId} #control_bar`).classList.remove('disabled')
    if(!response.ok){
      throw Error(response.statusText)
    }else{
      return response.json()
    }
  })
  
}