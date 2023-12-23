







const picture = document.querySelector('#cropper-image');
let isDragging = false;
let initialX;
let initialY;
let initialRotate = 0;

function getRotationValue() {
  const style = window.getComputedStyle(picture, null);
  const matrix = style.getPropertyValue('transform') || style.getPropertyValue('-webkit-transform');
  if (matrix && matrix !== 'none') {
    const values = matrix.split('(')[1].split(')')[0].split(',');
    const a = values[0];
    const b = values[1];
    const angle = Math.round(Math.atan2(b, a) * (180 / Math.PI));
    return angle;
  }
  return 0;
}



picture.addEventListener('mousedown', (e) => {
  isDragging = true;
  initialX = e.clientX;
  initialY = e.clientY;
  initialRotate = getRotationValue();
  picture.style.transition = 'none';
});


document.addEventListener('mousemove', (e) => {
  if (isDragging) {
    e.preventDefault();
    const deltaX = e.clientX - initialX;
    const deltaY = e.clientY - initialY;
    const newRotate = initialRotate + deltaX;
    picture.style.transform = `rotate(${newRotate}deg)`;
  }
});

document.addEventListener('mouseup', () => {
  if (isDragging) {
    isDragging = false;
    picture.style.transition = 'transform 0.3s';
  }
  console.log('Final rotation value:', getRotationValue());
});




