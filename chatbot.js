console.log("CHATBOT INIT");

function toggleChat() {
    let chatContainer = document.getElementById("chat-container");
    chatContainer.style.display = (chatContainer.style.display === "none" || chatContainer.style.display === "") ? "block" : "none";
}

let recognition;
let isListening = false;
let isWaitingForResponse = false;
let currentMenuElement = null;

if ("SpeechRecognition" in window || "webkitSpeechRecognition" in window) {
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
} else {
    console.error("Trình duyệt không hỗ trợ SpeechRecognition!");
    document.getElementById("mic-button").style.display = "none";
}

recognition.lang = 'vi-VN';
recognition.continuous = true;
recognition.interimResults = false;

recognition.onresult = function (event) {
    if (!isWaitingForResponse) {
        const speechText = event.results[event.results.length - 1][0].transcript.trim();
        if (speechText) {
            sendMessage(speechText);
        }
    }
};

recognition.onerror = function (event) {
    console.error("Lỗi nhận diện giọng nói:", event.error);
};

let micButton = document.getElementById("mic-button");
let sendButton = document.getElementById("button-send-mess");
let userInput = document.getElementById("user-input");

micButton.addEventListener("click", function () {
    if (!isListening && !isWaitingForResponse) {
        micButton.style.background = "green";
        recognition.start();
        isListening = true;
    } else {
        micButton.style.background = "red";
        recognition.abort();
        isListening = false;
    }
});

async function sendMessage(userInputText = null) {
    if (isWaitingForResponse) return;
    isWaitingForResponse = true;

    if (!userInputText) {
        userInputText = userInput.value.trim();
    }
    if (userInputText === '') {
        isWaitingForResponse = false;
        return;
    }

    appendMessage(userInputText, 'user');
    sendButton.disabled = true;
    micButton.disabled = true;
    userInput.disabled = true;

    const typingMessage = appendMessage("Chatbot đang gõ...", 'bot', true);

    const response = await fetch(
        "/Chatbot/getContent",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: userInput }),
        }
    );

	const data = await response.json();
	const message = data[0];

	removeMessage(typingMessage)
	
	// Nếu là dạng json_message từ custom action
	if (message.custom && message.custom.html) {
		// Thay đường dẫn ảnh trước khi hiển thị
		const updatedHtml = message.custom.html.replaceAll(`src='./`, `src='https://phanmemhui.com/`);
		appendMessage(updatedHtml, 'bot', true); // bật chế độ HTML
	} else {
		// Với text
		const text = message.text || JSON.stringify(message);
		appendMessage(text.replaceAll(`src='./`, `src='https://phanmemhui.com/`), 'bot');
	}

    isWaitingForResponse = false;
    sendButton.disabled = false;
    micButton.disabled = false;
    userInput.disabled = false;
    userInput.value = "";

    appendMessage("Anh/Chị muốn hỏi thêm gì không ?", 'bot');
    renderMenu(menuData);
    menuStack = [];
}

function appendMessage(message, sender, isTyping = false) {
    const chatBox = document.getElementById("chat-box");
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", sender + "-message");
    if (isTyping) {
        messageElement.setAttribute("id", "typing-indicator");
    }
    messageElement.innerHTML = message;
    chatBox.appendChild(messageElement);

    const isNearBottom = chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight < 100;

    if (isNearBottom) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    return messageElement;
}

function removeMessage(element) {
    if (element) element.remove();
}

userInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter" && !isWaitingForResponse) {
        event.preventDefault();
        sendMessage();
    }
});

const menuData = {
    "Phần mềm": {
        "Tải phần mềm": "cách tải phần mềm",
    },
    "Dây hụi": {
        "Hốt hụi": {
            "Cách hốt hụi": "cách hốt hụi",
            "Hốt hụi nhiều hội viên cùng kỳ": "cách hốt hụi nhiều người cùng kỳ"
        },
        "Tạo dây hụi": {
            "Dây hụi mới": "cách tạo dây hụi mới",
            "Dây hụi cho góp": "cách tạo dây hụi cho góp"
        },
        "Đóng tiền hụi": "cách đóng tiền hụi",
        "Dây hụi mãn": {
            "Mở dây hụi mãn hoạt động trở lại": "cách mở hụi mãn trở lại hoạt động",
            "Mãn dây hụi": "cách mãn dây hụi"
        },
        "Kỳ hốt/đóng": {
            "Xóa kỳ hốt hụi": "cách xóa hốt hụi",
            "Xóa kỳ hốt/đóng bị lỗi": "cách xóa kỳ hốt bị lỗi",
            "Thay đổi thông tin kỳ hốt hụi": "cách thay đổi thông tin kỳ hốt hụi",
        }

    },
    "Hội viên": {
        "Gom hội viên bị trùng": "cách gom hội viên bị trùng",
        "Thay đổi thông tin hội viên": "cách thay đổi hội viên",
        "thêm hội viên/số phần hụi": "cách thêm số phần hụi",
        "giảm hội viên/số phần hụi": "cách giảm số phần hụi",
    },
    "Tất toán hụi": {
        "Tất toán hụi sống (san/bán dây hụi)": "cách tất toán hụi sống",
        "Tất toán hụi chết (đúp dây hụi)": "cách tất toán hụi chết",
        "xóa tất toán/đúp dây hụi": "cách xóa tất toán hụi chết",
        "Khôi phục tất toán (hủy đúp dây hụi)": "cách phục hồi tất toán hụi chết"
    },
    "Hóa đơn": {
        "In hóa đơn/Bill": "in hóa đơn"
    },
    "Bảng âm dương": {
        "Xem cân bằng âm dương của hội viên": "cách cân bằng âm dương",
        "Đóng lại hụi cũ để tính cân bằng chính xác": "cách đóng lại hụi cũ"
    }
};

let menuStack = [];

function renderMenu(currentData) {
    const chatBox = document.getElementById("chat-box");
    const oldMenus = chatBox.querySelectorAll(".menu-message");
    oldMenus.forEach(menu => menu.remove());

    const menuMessage = document.createElement("div");
    menuMessage.classList.add("message", "menu-message");

    const container = document.createElement("div");
    for (const key in currentData) {
        const btn = document.createElement('button');
        btn.textContent = key;
        btn.classList.add("menu-button");
        btn.onclick = () => handleMenuClick(currentData[key], key);
        container.appendChild(btn);
    }

    if (menuStack.length > 0) {
        const backBtn = document.createElement("button");
        backBtn.textContent = "🔙 Quay lại";
        backBtn.classList.add("menu-button"); backBtn.classList.add("menu-button", "back-button");
        backBtn.onclick = () => {
            menuStack.pop();
            const previousMenu = menuStack.length > 0 ? menuStack[menuStack.length - 1].data : menuData;
            renderMenu(previousMenu);
        };
        container.appendChild(backBtn);
    }

    menuMessage.appendChild(container);
    chatBox.appendChild(menuMessage);
    chatBox.scrollTop = chatBox.scrollHeight;
    currentMenuElement = menuMessage;
}

function handleMenuClick(next, label) {
    if (typeof next === 'string') {
        if (currentMenuElement) currentMenuElement.remove();
        sendMessage(next); // chỉ gửi và hiển thị nội dung được gán
        menuStack = [];
        currentMenuElement = null;
    } else {
        menuStack.push({ data: next, label });
        renderMenu(next);
    }
}


window.onload = function () {
    appendMessage("Bạn cần giúp gì? Hãy chọn một mục bên dưới.", 'bot');
    renderMenu(menuData);
};
