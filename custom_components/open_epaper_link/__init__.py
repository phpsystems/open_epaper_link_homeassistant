from __future__ import annotations
from .imagegen import *
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from . import hub
from .const import DOMAIN
import logging
import pprint

_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    # callback for the image downlaod service
    async def drawcustomservice(service: ServiceCall) -> None:
        ip = hass.states.get(DOMAIN + ".ip").state 
        entity_ids = service.data.get("entity_id")
        for entity_id in entity_ids:
            _LOGGER.info("Called entity_id: %s" % (entity_id))
            imgbuff = customimage(entity_id, service, hass)
            id = entity_id.split(".")
            result = await hass.async_add_executor_job(uploadimg, imgbuff, id[1], ip)

    # callback for the image downlaod service
    async def dlimg(service: ServiceCall) -> None:
        ip = hass.states.get(DOMAIN + ".ip").state 
        entity_ids = service.data.get("entity_id")
        dither = service.data.get("dither", False)
        for entity_id in entity_ids:
            _LOGGER.info("Called entity_id: %s" % (entity_id))
            id = entity_id.split(".")
            imgbuff = await hass.async_add_executor_job(downloadimg, entity_id, service, hass)
            result = await hass.async_add_executor_job(uploadimg, imgbuff, id[1], ip, dither)

    # callback for the image downlaod service
    async def displayimg(service: ServiceCall) -> None:
        ip = hass.states.get(DOMAIN + ".ip").state 
        entity_ids = service.data.get("entity_id")
        dither = service.data.get("dither", False)
        for entity_id in entity_ids:
            _LOGGER.info("Called entity_id: %s" % (entity_id))
            id = entity_id.split(".")
            imgbuff = await hass.async_add_executor_job(dispimg, entity_id, service, hass)
            result = await hass.async_add_executor_job(uploadimg, imgbuff, id[1], ip, dither)
    
    # callback for the 5 line service
    async def lines5service(service: ServiceCall) -> None:
        ip = hass.states.get(DOMAIN + ".ip").state

        entity_ids = service.data.get("entity_id")
        for entity_id in entity_ids:
            _LOGGER.info("Called entity_id: %s" % (entity_id))
            imgbuff = gen5line(entity_id, service, hass)
            id = entity_id.split(".")
            result = await hass.async_add_executor_job(uploadimg, imgbuff, id[1], ip)

    # callback for the 4 line service
    async def lines4service(service: ServiceCall) -> None:
        ip = hass.states.get(DOMAIN + ".ip").state

        entity_ids = service.data.get("entity_id")
        for entity_id in entity_ids:
            _LOGGER.info("Called entity_id: %s" % (entity_id))
            imgbuff = gen4line(entity_id, service, hass)
            id = entity_id.split(".")
            result = await hass.async_add_executor_job(uploadimg, imgbuff, id[1], ip)
            
    # callback for the setled service
    async def setled(service: ServiceCall) -> None:
        ip = hass.states.get(DOMAIN + ".ip").state

        entity_ids = service.data.get("entity_id")
        for entity_id in entity_ids:
            _LOGGER.info("Called entity_id: %s" % (entity_id))
            id = entity_id.split(".")
            color = service.data.get("color", "")
            cmd = ""
            if(color == "off"): cmd = "{\"cmd\":\"100\"}"
            if(color == "red"): cmd = "{\"cmd\":\"101\"}"
            if(color == "green"): cmd = "{\"cmd\":\"102\"}"
            if(color == "blue"): cmd = "{\"cmd\":\"103\"}"
            if(color == "yellow"): cmd = "{\"cmd\":\"104\"}"
            if(color == "cyan"): cmd = "{\"cmd\":\"105\"}"
            if(color == "magenta"): cmd = "{\"cmd\":\"106\"}"
            if(color == "white"): cmd = "{\"cmd\":\"107\"}"
            result = await hass.async_add_executor_job(uploadcfg, cmd, id[1], "17",ip)

    # register the services
    hass.services.register(DOMAIN, "dlimg", dlimg)
    hass.services.register(DOMAIN, "displayimg", displayimg)
    hass.services.register(DOMAIN, "lines5", lines5service)
    hass.services.register(DOMAIN, "lines4", lines4service)
    hass.services.register(DOMAIN, "drawcustom", drawcustomservice)
    hass.services.register(DOMAIN, "setled", setled)
    # error haneling needs to be improved
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub.Hub(hass, entry.data["host"], entry)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

