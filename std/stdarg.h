#define va_list void*
#define va_start(ap, last) (ap = _VARLIST_)
#define va_arg(ap, type) ((type)*ap++) // add cast
#define va_end(ap) (ap = 0)