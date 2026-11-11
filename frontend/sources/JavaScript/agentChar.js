const canvas = document.getElementById("agentCanvas");
const ctx = canvas.getContext("2d");

const img = new Image();
img.src = "../../asset/Claude/claude-rice.webp";

img.onload = () => {
  const columns = 8;
  const rows = 15;
  const frameWidth = img.width / columns;
  const frameHeight = img.height / rows;

  let currentFrame = 0;

  setInterval(() => {
    const col = currentFrame % columns;
    const row = Math.floor(currentFrame / columns);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(
      img,
      col * frameWidth,
      row * frameHeight,
      frameWidth,
      frameHeight,
      0,
      0,
      canvas.width,
      canvas.height
    );

    currentFrame = (currentFrame + 1) % (columns * rows);
  }, 1000 / 12);
};