function deleteArticle(postSlug) {
    var confirmation = confirm('Bu makaleyi silmek istediğinizden emin misiniz?');

    if (confirmation) {
        $.ajax({
            url: '/delete_article/' + postSlug,
            type: 'DELETE',
            success: function(result) {
                window.location.reload();
            },
            error: function(error) {
                console.error('Error:', error);
                window.location.reload();
            }
        });
    }
}

function updateArticle(postSlug) {
    var form = document.querySelector('form');

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        var formData = new FormData(form);

        $.ajax({
            url: '/edit_article/' + postSlug,
            type: 'PUT',
            data: formData,
            processData: false,
            contentType: false,
            success: function (result) {
                window.location = '/dashboard'
            },
            error: function (error) {
                console.error('Error:', error);
            }
        });
    });
}

function editProfile(username) {
    var form = document.querySelector('form');

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        var formData = new FormData(form);

        $.ajax({
            url: '/edit_profile/' + username,
            type: 'PUT',
            data: formData,
            processData: false,
            contentType: false,
            success: function (result) {
                window.location = '/user/' + username
            },
            error: function (error) {
                console.error('Error:', error);
            }
        });
    });
}

function deleteUser(userId) {
    var confirmation = confirm('Bu kullanıcıyı silmek istediğinizden emin misiniz?');

    if (confirmation) {
        $.ajax({
            url: '/delete_user/' + userId,
            type: 'DELETE',
            success: function(result) {
                window.location.reload();
            },
            error: function(error) {
                console.error('Error:', error);
                window.location.reload();
            }
        });
    }
}

function deleteCategory(categoryId) {
    var confirmation = confirm('Bu kategoriyi silmek istediğinizden emin misiniz?');

    if (confirmation) {
        $.ajax({
            url: '/delete_category/' + categoryId,
            type: 'DELETE',
            success: function(result) {
                window.location.reload();
            },
            error: function(error) {
                console.error('Error:', error);
                window.location.reload();
            }
        });
    }
}

function editCategory(categorySlug) {
    var form = document.querySelector('form');

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        var formData = new FormData(form);

        $.ajax({
            url: '/edit_category/' + categorySlug,
            type: 'PUT',
            data: formData,
            processData: false,
            contentType: false,
            success: function (result) {
                window.location = '/get_categories'
            },
            error: function (error) {
                console.error('Error:', error);
            }
        });
    });
}

const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;

function toggleDarkMode() {
    body.classList.toggle('dark-mode');
    
    let newTheme = '';
    darkModeToggle.checked ? newTheme = 'dark-mode' : newTheme = 'light-mode';

    updateTheme(newTheme, function() {
        window.location.reload();
    });
}

darkModeToggle.addEventListener('change', toggleDarkMode);

function updateTheme(theme, callback) {
    $.ajax({
        type: 'POST',
        url: '/cookie',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({'theme': theme}),
        success: function() {
            if (typeof callback === 'function') {
                callback();
            }
        },
        error: function() {
            
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    var contentElement = document.getElementById('content');
    if (contentElement) {
        CKEDITOR.replace('content');
    }
});

function toggleNav() {
    var sidebar = document.getElementById("mySidebar");
    var main = document.getElementById("main");
    var openButton = document.getElementById("openButton");
    
    if (sidebar.style.width === "250px") {
        sidebar.style.width = "0";
        main.style.marginLeft = "0";
        openButton.innerHTML = "☰";
        openButton.style.position = "absolute";
        document.body.style.overflow = "auto";
    } else {
        sidebar.style.width = "250px";
        main.style.marginLeft = "250px";
        openButton.innerHTML = "×";
        openButton.style.position = "fixed";
        document.body.style.overflow = "hidden";
    }
}

$(".custom-file-input").on("change", function() {
    var fileName = $(this).val().split("\\").pop();
    $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
});
