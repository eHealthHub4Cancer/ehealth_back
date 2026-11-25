/* Reduce large portraits before submitting them through the production proxy. */
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('id_image');
  if (!input) return;
  const message = document.createElement('p');
  message.setAttribute('role', 'status');
  message.setAttribute('aria-live', 'polite');
  input.after(message);
  const limit = 5 * 1024 * 1024;
  let revision = 0;
  input.addEventListener('change', async () => {
    const current = ++revision;
    const file = input.files[0];
    input.setCustomValidity('');
    message.textContent = '';
    if (!file || file.size <= 1024 * 1024) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      if (file.size > limit) {
        input.setCustomValidity('Choose an image smaller than 5 MB, or use JPEG, PNG, or WebP.');
        message.textContent = input.validationMessage;
      }
      return;
    }
    input.setCustomValidity('Please wait for your portrait to finish resizing.');
    message.textContent = 'Preparing your portrait… Please wait before saving.';
    const url = URL.createObjectURL(file);
    try {
      const image = new Image();
      image.src = url;
      await image.decode();
      if (current !== revision) return;
      const scale = Math.min(1, 1600 / Math.max(image.naturalWidth, image.naturalHeight));
      const canvas = document.createElement('canvas');
      canvas.width = Math.max(1, Math.round(image.naturalWidth * scale));
      canvas.height = Math.max(1, Math.round(image.naturalHeight * scale));
      const context = canvas.getContext('2d');
      context.fillStyle = '#ffffff';
      context.fillRect(0, 0, canvas.width, canvas.height);
      context.drawImage(image, 0, 0, canvas.width, canvas.height);
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.85));
      if (current !== revision) return;
      if (!blob || blob.size > limit) throw new Error('Image could not be reduced enough.');
      const transfer = new DataTransfer();
      transfer.items.add(new File([blob], file.name.replace(/\.[^.]+$/, '') + '.jpg', {type: 'image/jpeg'}));
      input.files = transfer.files;
      input.setCustomValidity('');
      message.textContent = `Portrait ready: ${(blob.size / 1024).toFixed(0)} KB, ${canvas.width} × ${canvas.height} pixels. Saved as JPEG with a white background.`;
    } catch (error) {
      if (current !== revision) return;
      if (file.size > limit) input.setCustomValidity('Unable to resize this image. Please choose a portrait smaller than 5 MB.');
      else input.setCustomValidity('');
      message.textContent = file.size > limit ? input.validationMessage : 'Using the original image; automatic resizing was unavailable.';
    } finally {
      URL.revokeObjectURL(url);
    }
  });
});
