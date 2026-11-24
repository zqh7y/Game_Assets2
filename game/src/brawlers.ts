// The roster and where each brawler stands near the castle.

export type BrawlerName =
  | 'Rook'
  | 'Bram'
  | 'Hood'
  | 'Barley'
  | 'Wick'
  | 'Ash'
  | 'Sage'
  | 'Chop'
  | 'Tusk'
  | 'Pip'
  | 'Fuse'
  | 'Jinx';

export interface BrawlerSpawn {
  name: BrawlerName;
  /** Feet position in world pixels on the 4096 map. */
  x: number;
  y: number;
  /** The art faces right; true mirrors it. */
  faceLeft: boolean;
}

// The courtyard ring spans roughly x 1660-2480, y 1640-2290; the castle itself
// covers x 1870-2370, y 1530-2090. Brawlers stand on the cobblestones in front of
// and beside it, inside x 1760-2450 so the whole group fits the starting view.
export const SPAWNS: BrawlerSpawn[] = [
  { name: 'Rook', x: 1790, y: 1965, faceLeft: false },
  { name: 'Bram', x: 1800, y: 2065, faceLeft: false },
  { name: 'Hood', x: 1890, y: 2140, faceLeft: false },
  { name: 'Barley', x: 1990, y: 2105, faceLeft: false },
  { name: 'Wick', x: 1980, y: 2210, faceLeft: false },
  { name: 'Ash', x: 2080, y: 2240, faceLeft: false },
  { name: 'Sage', x: 2110, y: 2140, faceLeft: true },
  { name: 'Chop', x: 2185, y: 2225, faceLeft: true },
  { name: 'Tusk', x: 2235, y: 2105, faceLeft: true },
  { name: 'Pip', x: 2290, y: 2185, faceLeft: true },
  { name: 'Fuse', x: 2355, y: 2090, faceLeft: true },
  { name: 'Jinx', x: 2410, y: 1985, faceLeft: true },
];

/** Sheets: 4 columns x 2 rows (row 1 walk, row 2 attack: a shot, or a swing for Bram, Ash and Chop). */
export const SHEET = { cols: 4, rows: 2 };

// Vite bundles the sheets straight from the repo's animations/ folder.
const sheetUrls = import.meta.glob<string>('../../animations/*/*_sheet_right.png', {
  eager: true,
  query: '?url',
  import: 'default',
});

export function sheetUrl(name: BrawlerName): string {
  const key = `../../animations/${name}/${name}_sheet_right.png`;
  const url = sheetUrls[key];
  if (!url) throw new Error(`Missing sheet for ${name}`);
  return url;
}
