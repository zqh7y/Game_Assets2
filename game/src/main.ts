import Phaser from 'phaser';
import { BACKGROUND_COLOR, GAME_HEIGHT, GAME_WIDTH } from './config';
import { MapScene } from './scenes/MapScene';

const game = new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  backgroundColor: BACKGROUND_COLOR,
  scale: {
    // EXPAND keeps the 9:16 size as a minimum and grows to fill taller phones.
    // index.html limits the container to 9:16 on wide screens.
    mode: Phaser.Scale.EXPAND,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    width: GAME_WIDTH,
    height: GAME_HEIGHT,
  },
  input: { activePointers: 3 },
  scene: [MapScene],
});

// Show the controls hint once the map is up, then fade it on the first touch or after a while.
game.events.once('map-ready', () => {
  const hint = document.getElementById('hint');
  if (!hint) return;
  hint.classList.add('visible');
  const hide = () => hint.classList.remove('visible');
  window.setTimeout(hide, 6000);
  window.addEventListener('pointerdown', hide, { once: true });
  window.addEventListener('wheel', hide, { once: true });
});
