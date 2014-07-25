/*
 * This source is borrowed from following link
 * https://github.com/jart/fabulous/blob/master/fabulous/_xterm256.c
 * I make a slightly change to fit my module here
 */
typedef struct {
        int r;
        int g;
        int b;
} rgb_t;
int CUBE_STEPS[] = { 0x00, 0x5F, 0x87, 0xAF, 0xD7, 0xFF };
rgb_t BASIC16[] =
      { {   0,   0,   0 }, { 205,   0,   0}, {   0, 205,   0 },
        { 205, 205,   0 }, {   0,   0, 238}, { 205,   0, 205 },
        {   0, 205, 205 }, { 229, 229, 229}, { 127, 127, 127 },
        { 255,   0,   0 }, {   0, 255,   0}, { 255, 255,   0 },
        {  92,  92, 255 }, { 255,   0, 255}, {   0, 255, 255 },
        { 255, 255, 255 } };
rgb_t COLOR_TABLE[256];


rgb_t ansi_to_rgb(int xcolor)
{
  rgb_t res;
  if (xcolor < 16) {
    res = BASIC16[xcolor];
  } else if (16 <= xcolor && xcolor <= 231) {
    xcolor -= 16;
    res.r = CUBE_STEPS[(xcolor / 36) % 6];
    res.g = CUBE_STEPS[(xcolor / 6) % 6];
    res.b = CUBE_STEPS[xcolor % 6];
  } else if (232 <= xcolor && xcolor <= 255) {
    res.r = res.g = res.b = 8 + (xcolor - 232) * 0x0A;
  }
  return res;
}

int init()
{
  int c;
  for (c = 0; c < 256; c++) {
    COLOR_TABLE[c] = ansi_to_rgb(c);
  }
  return 0;
}

int rgb_to_ansi(int r, int g, int b)
{
  int best_match = 0;
  int smallest_distance = 1000000000;
  int c, d;
  for (c = 16; c < 256; c++) {
    d = (COLOR_TABLE[c].r - r)*(COLOR_TABLE[c].r - r) +
        (COLOR_TABLE[c].g - g)*(COLOR_TABLE[c].g - g) +
        (COLOR_TABLE[c].b - b)*(COLOR_TABLE[c].b - b);
    if (d < smallest_distance) {
      smallest_distance = d;
      best_match = c;
    }
  }
  return best_match;
}
