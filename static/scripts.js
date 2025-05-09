document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("postModal");
    const openBtn = document.getElementById("openModalBtn");
    const closeBtn = document.getElementById("closeModalBtn");

    if (openBtn && modal && closeBtn) {
        openBtn.addEventListener("click", function () {
            modal.style.display = "block";
        });

        closeBtn.addEventListener("click", function () {
            modal.style.display = "none";
        });

        window.addEventListener("click", function (event) {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    }

    const imageInput = document.getElementById("imageInput");
    const previewImage = document.getElementById("previewImage");

    if (imageInput && previewImage) {
        imageInput.addEventListener("change", function () {
            const file = imageInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImage.src = e.target.result;
                    previewImage.style.display = "block";
                };
                reader.readAsDataURL(file);
            } else {
                previewImage.src = "";
                previewImage.style.display = "none";
            }
        });
    }
});

// Функция переключения показа поля ввода хэштегов
function toggleHashtags() {
    const input = document.getElementById('hashtagsInput');
    if (input) {
        input.style.display = input.style.display === 'none' ? 'block' : 'none';
    }
}




function toggleLike(postId) {
    fetch(`/account/like_post/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    })
    .then(async response => {
        const text = await response.text();
        try {
            const data = JSON.parse(text);
            if (response.status === 400 && data.error) {
                alert(data.error);
                return;
            }

            const likeIcon = document.getElementById(`like-icon-${postId}`);
            const likeCount = document.getElementById(`likes-count-${postId}`);

            likeCount.textContent = data.likes_count;

            if (data.liked) {
                likeIcon.src = likeIcon.dataset.likedSrc;
            } else {
                likeIcon.src = likeIcon.dataset.unlikedSrc;
            }
        } catch (e) {
            //console.error("Сервер вернул не JSON:", text);
        }
    })
    .catch(error => {
        console.error('Ошибка при отправке лайка:', error);
    });
}

