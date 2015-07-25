from importd import d
import websktop

@d("/")
def idx(request):
    return "index.html"

if __name__ in "__main__":
    websktop.main(d)
