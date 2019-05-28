/*
 * This source is borrowed from following link
 * https://github.com/jart/fabulous/blob/master/fabulous/_xterm256.c
 * I make a slightly change to fit my module here
 */
 
#include <Python.h>
 
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

/* __declspec(dllexport) */

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

// int rgb_to_ansi(int r, int g, int b)
PyObject *
rgb_to_ansi(PyObject *self, PyObject *args)
{
    int r, g, b;
    
    if (!PyArg_ParseTuple(args, "iii", &r, &g, &b)) {
        return NULL;
    }
    
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
    
    return Py_BuildValue("i", best_match);
}

int init()
{
  int c;
  for (c = 0; c < 256; c++) {
    COLOR_TABLE[c] = ansi_to_rgb(c);
  }
  return 0;
}

static PyMethodDef ImageMethods[] = {
    {"rgb_to_ansi",  (PyCFunction) rgb_to_ansi, METH_VARARGS, "Convert RGB to ANSI"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef ImageModule = {
    PyModuleDef_HEAD_INIT,
    "rainbowstream_image",   /* name of module */
    NULL,  /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    ImageMethods
};

PyMODINIT_FUNC
PyInit_rainbowstream_image(void)
{     
    PyObject *m;
    
    m = PyModule_Create(&ImageModule);
    if (m == NULL) {
        return NULL;
    }
    
    init();
    
    return m;
}
