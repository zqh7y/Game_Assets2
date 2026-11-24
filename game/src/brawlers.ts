// The roster and where each brawler stands near the castle.

export type BrawlerName =
  | 'Beam'
  | 'Dough'
  | 'Soot'
  | 'Honey'
  | 'Nana'
  | 'Capy'
  | 'Pango'
  | 'Bill'
  | 'Tardi'
  | 'Octo'
  | 'Mossy';

export interface BrawlerSpawn {
  name: BrawlerName;
  /** Feet position in world pixels on the 4096 map. */
  x: number;
  y: number;
  /** The art faces right; true mirrors it. */
  faceLeft: boolean;
  /**
   * On-map height in world pixels. The armed sheets were cut at different
   * scales, so each brawler gets its own target height instead of one shared scale.
   */
  height: number;
}

// The courtyard ring spans roughly x 1660-2480, y 1640-2290; the castle itself
// covers x 1870-2370, y 1530-2090. Brawlers stand on the cobblestones in front of
// it, inside x 1780-2370 so the whole group fits the starting view.
export const SPAWNS: BrawlerSpawn[] = [
  { name: 'Beam', x: 1795, y: 1975, faceLeft: false, height: 98 },
  { name: 'Soot', x: 1805, y: 2075, faceLeft: false, height: 90 },
  { name: 'Dough', x: 1890, y: 2150, faceLeft: false, height: 104 },
  { name: 'Mossy', x: 1990, y: 2105, faceLeft: false, height: 84 },
  { name: 'Honey', x: 1985, y: 2215, faceLeft: false, height: 100 },
  { name: 'Nana', x: 2085, y: 2240, faceLeft: false, height: 92 },
  { name: 'Octo', x: 2135, y: 2125, faceLeft: true, height: 84 },
  { name: 'Capy', x: 2190, y: 2215, faceLeft: true, height: 100 },
  { name: 'Bill', x: 2250, y: 2090, faceLeft: true, height: 98 },
  { name: 'Pango', x: 2285, y: 2180, faceLeft: true, height: 80 },
  { name: 'Tardi', x: 2360, y: 2085, faceLeft: true, height: 86 },
];

/** Armed sheets: 4 columns x 2 rows (row 1 walk with the weapon, row 2 shoot or melee swing). */
export const ARMED_SHEET = { cols: 4, rows: 2 };

// Vite bundles the sheets straight from the repo's animations/ folder.
const armedSheetUrls = import.meta.glob<string>('../../animations/*/*_armed_sheet_right.png', {
  eager: true,
  query: '?url',
  import: 'default',
});

export function armedSheetUrl(name: BrawlerName): string {
  const key = `../../animations/${name}/${name}_armed_sheet_right.png`;
  const url = armedSheetUrls[key];
  if (!url) throw new Error(`Missing armed sheet for ${name}`);
  return url;
}
