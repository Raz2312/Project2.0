// dialog
const dialog = document.getElementById('dialog');
const wrapper = document.querySelector('.wrapper');
const showLoginDialog = (show) => show ? dialog.showModal() : dialog.close();
dialog.addEventListener('click', (e) => !wrapper.contains(e.target) && dialog.close());







function previewImage(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var imagePreview = document.getElementById('imagePreview');
            imagePreview.innerHTML = `<img src="${e.target.result}" style="width: 100%; height: 100%; object-fit: contain; border-radius: 8px;">`;
            imagePreview.classList.add('has-image');
        }
        reader.readAsDataURL(input.files[0]);
    }
}



