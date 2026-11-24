import Phaser from 'phaser';
import { Brawler, sheetKey } from '../Brawler';
import { SPAWNS, sheetUrl } from '../brawlers';
import { CameraControl } from '../CameraControl';
import { MAP_TILES_PER_SIDE, MAP_TILE_SIZE, START_VIEW, ZOOM } from '../config';

const mapTileKey = (tx: number, ty: number) => `map_${tx}_${ty}`;

/** The castle island map you can scroll and zoom, with the brawlers near the castle. */
export class MapScene extends Phaser.Scene {
  private brawlers: Brawler[] = [];
  private cameraControl!: CameraControl;

  constructor() {
    super('map');
  }

  preload(): void {
    this.showLoadingBar();
    for (let ty = 0; ty < MAP_TILES_PER_SIDE; ty++) {
      for (let tx = 0; tx < MAP_TILES_PER_SIDE; tx++) {
        this.load.image(mapTileKey(tx, ty), `map/${mapTileKey(tx, ty)}.jpg`);
      }
    }
    for (const spawn of SPAWNS) {
      this.load.image(sheetKey(spawn.name), sheetUrl(spawn.name));
    }
  }

  create(): void {
    for (let ty = 0; ty < MAP_TILES_PER_SIDE; ty++) {
      for (let tx = 0; tx < MAP_TILES_PER_SIDE; tx++) {
        this.add
          .image(tx * MAP_TILE_SIZE, ty * MAP_TILE_SIZE, mapTileKey(tx, ty))
          .setOrigin(0, 0)
          .setDepth(-1);
      }
    }

    this.brawlers = SPAWNS.map((spawn) => new Brawler(this, spawn));

    this.cameraControl = new CameraControl(this);
    this.cameraControl.centerOn(START_VIEW.x, START_VIEW.y, ZOOM.start);
    this.cameraControl.onTap = (x, y) => this.brawlerAt(x, y)?.attack();

    this.game.events.emit('map-ready');
  }

  update(_time: number, delta: number): void {
    this.cameraControl.update(delta);
  }

  /** The front-most brawler under a world point. */
  private brawlerAt(x: number, y: number): Brawler | undefined {
    return this.brawlers
      .filter((b) => b.hitArea.contains(x, y))
      .sort((a, b) => b.sprite.depth - a.sprite.depth)[0];
  }

  private showLoadingBar(): void {
    const { width, height } = this.cameras.main;
    const barW = width * 0.6;
    const barH = 18;
    const x = (width - barW) / 2;
    const y = height / 2;
    const track = this.add.rectangle(x, y, barW, barH, 0xffffff, 0.15).setOrigin(0, 0.5);
    const fill = this.add.rectangle(x, y, 0, barH, 0xffffff, 0.9).setOrigin(0, 0.5);
    this.load.on(Phaser.Loader.Events.PROGRESS, (p: number) => {
      fill.width = barW * p;
    });
    this.load.once(Phaser.Loader.Events.COMPLETE, () => {
      track.destroy();
      fill.destroy();
    });
  }
}
