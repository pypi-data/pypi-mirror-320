from flet import Page
from .xstate import Xstate
from .xview import Xview
from .xparams import Xparams
from .xmiddleware import Xmiddleware
from .view_not_found import NotFoundView
from .view_internal_error import InternalErrorView
from repath import match
import traceback


def route(route:str,view:Xview) -> dict:
    return {"route":route,"view":view}

def route_str(route):
    if type(route) == str:
        return route
    else:
        return str(route.route)

class Xapp:
    def __init__(
            self,
            page:Page,
            routes:list[route],
            state:Xstate = None,
            middleware:Xmiddleware = None,
            init_route:str = None,
            not_found_view :Xview= NotFoundView,
            internal_error_view :Xview= InternalErrorView,
            debug :bool= True,
            ):
        self.__debug = debug
        self.__page = page
        self.__middleware = middleware
        self.__routes = routes
        self.__params = Xparams()
        self.__404_not_found_view = not_found_view
        self.__internal_error_view = internal_error_view
        page.on_route_change = self.route_event_handler
        page.views.pop()

        if state!=None:
            self.__state = state(page)
        else:
            self.__state = Xstate(page)

        if init_route!=None:
            self.__page.go(init_route)
        else:
            self.__page.go(self.__page.route)

    def route_event_handler(self,route):

        try:
            route_match = None

            for r in self.__routes:
                route_match = match(r["route"], route_str(route))
                if route_match:
                    self.__params = Xparams(route_match.groupdict())
                    # if middleware is provided then call
                    if self.__middleware != None:
                        middleware = self.__middleware(page=self.__page,state=self.__state,params=self.__params)
                        middleware.middleware()
                    # if redirect route in midellware
                    if self.__page.route != route_str(route=route):
                        self.__page.go(self.__page.route)
                        return
                    view = r["view"](page=self.__page,state = self.__state,params=self.__params)
                    self.__page.views.append(view.build())
                    self.__page.update()
                    view.onBuildComplete()
                    break

            if route_match == None:
                view = self.__404_not_found_view(page=self.__page,state = self.__state,params=Xparams())
                view.debug = self.__debug
                self.__page.views.append(view.build())
                self.__page.update()
                view.onBuildComplete()

        except Exception as e:
            view = self.__internal_error_view(page=self.__page,state = self.__state,params=Xparams())
            view.debug = self.__debug
            view.error = traceback.format_exc(110)
            self.__page.views.append(view.build())
            self.__page.update()
            view.onBuildComplete()

