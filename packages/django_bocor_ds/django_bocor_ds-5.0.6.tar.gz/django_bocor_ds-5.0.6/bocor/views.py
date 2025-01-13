from shared_lib import utils
from _data import bocor, shared_lib

c = bocor.context
c.update(shared_lib.analytics)


def bocor_home(request):
    return utils.home(request,'bocor/index.html', c)

def bocor_terms(request):
    return utils.terms(request, 'bocor/pages/terms.html', c)

def bocor_privacy(request):
    return utils.privacy(request, 'bocor/pages/privacy.html', c)

def bocor_portfolio_details(request, pk):
    return utils.portfolio_details(request, 'bocor/pages/portfolio_details.html', pk, c)
