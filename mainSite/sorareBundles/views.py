from django.http import HttpResponse
from sorareBundles.scripts import getAllBundledAuctions
from sorareBundles.scripts import getPlayersData
from sorareBundles.scripts.init.bundle import initAndGetBundlesData
import json
import html
from urllib.parse import unquote


def index(request):
    bundles = getAllBundledAuctions.get_all_bundles()
    return HttpResponse(bundles)


def getPlayersAverage(request):
    names = request.body
    names = unquote(names)
    averages = getPlayersData.getPlayersData(json.loads(names))
    return HttpResponse(json.dumps(averages))


def getExtraPlayerData(request):
    players_id = request.body
    players_id = unquote(players_id)
    data = getPlayersData.getExtraPlayerData(json.loads(players_id))
    return HttpResponse(json.dumps(data))


def initData(request):
    data = initAndGetBundlesData()
    return HttpResponse(json.dumps(data))
