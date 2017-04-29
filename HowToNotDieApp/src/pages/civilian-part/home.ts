import { Component, ElementRef } from '@angular/core';

import { NavController, NavParams } from 'ionic-angular';

import { ItemDetailsPage } from '../item-details/item-details';

import { $WebSocket } from 'angular2-websocket/angular2-websocket';
import { BackgroundMode } from '@ionic-native/background-mode';
import { Geolocation } from '@ionic-native/geolocation';

declare var H: any;

@Component({
  selector: 'civilian-part',
  templateUrl: 'home.html'
})
export class CivilianPartPage {
    public  danger: boolean = false;

    platform: any;
    defaultLayers: any;
    map: any;
    behavior: any;
    ui: any;
    bubble: any;
    mapContainer: any;
    ws: $WebSocket;
    private pathForWebSockets: string = "162.243.253.201:8123/chat/";
    public run: boolean = true;
    currentLocation: any;
    canMove: boolean;

    sendMessage(text: String): void {
        console.log("sending : " + text);
        this.ws.send(text).subscribe(
            (msg)=> {
                console.log("next", msg.data);
            },
            (msg)=> {
                console.log("error", msg);
            },
            ()=> {
                console.log("complete");
            }
        );
    }

    constructor(public navCtrl: NavController, private elRef: ElementRef, private backgroundMode: BackgroundMode, private geolocation: Geolocation, public navParams: NavParams) {
        console.log("arrived on civilian-part");

        H.geo.Rect.prototype.getBoundingPoints = function() {
            var top = this.getTop();
            var bottom = this.getBottom();
            var left = this.getLeft();
            var right = this.getRight();
            //console.log(top + "," + bottom + "," + left + "," + right);
            return [new H.geo.Point(top, left), new H.geo.Point(top, right), new H.geo.Point(bottom, right), new H.geo.Point(bottom, left)];
        }

        function addWaypoint(dict, point, index, geo = true, type = "passThrough", transitRadius = null, userLabel = null, useAlt = false) {
            //console.log("begin addWaypoint");
            dict['waypoint' + index] = (geo ? "geo!" : "") + (type ? (type + "!") : "") + point.lat + "," + point.lng + (useAlt ? (',' + point.alt) : "") + (transitRadius ? (";" + transitRadius) : "") + (userLabel ? (";" + userLabel) : "");
            //console.log("end addWaypoint");
        };

        function addAvoidArea(dict, area, useAlt = false) {
            var topLeft = area.getTopLeft();
            var bottomRight = area.getBottomRight();
            dict['avoidareas'] += topLeft.lat + ',' + topLeft.lng + (useAlt ? (',' + topLeft.alt) : "") + ';' + bottomRight.lat + ',' + bottomRight.lng + (useAlt ? (',' + bottomRight.alt) : "") + '!';
        };

        function addAvoidAreas(dict, areas, useAlt = false) {
            //console.log("begin addAvoidAreas");
            //console.log(areas);
            if(areas.length != 0) {
                dict['avoidareas'] = "";
                for(var i = 0 ; i < areas.length ; i++) {
                    //console.log(areas[i]);
                    addAvoidArea(dict, areas[i], useAlt);
                }
                dict['avoidareas'] = dict['avoidareas'].substring(0, dict['avoidareas'].length-1);
            }
            //console.log("end addAvoidAreas");
        };

        function addDestination(dict, safeZone) {
            addWaypointFromList(dict, safeZone.point, 1, true, "stopOver", safeZone.radius);
        };

        function addWaypointFromList(dict, point, index, geo = true, type = "passThrough", transitRadius = null, userLabel = null, useAlt = false) {
            console.log("destination radius : " + transitRadius);
            dict['waypoint' + index] = (geo ? "geo!" : "") + (type ? (type + "!") : "") + point[0] + "," + point[1] + (useAlt ? (',' + point[2]) : "") + (transitRadius ? (";" + transitRadius) : "") + (userLabel ? (";" + userLabel) : "");
        };

        function error(error) {
            alert('Ooops!');
        };

        H.service.Platform.prototype.calculateRoute = function (mode = 'fastest;car', representation = 'display', routeAttributes = 'waypoints,summary,shape,legs', maneuverAttributes = 'direction,action', destination, onSuccess : (response: any) => void, onError  : (response: any) => void, avoidAreas  : String, alternatives = 0, jsonAttributes = 73) {
            var router = this.getRoutingService(),
                routeRequestParams = {
                    mode: mode,
                    representation: representation,
                    routeattributes : routeAttributes,
                    maneuverattributes: maneuverAttributes,
                    alternatives: alternatives,
                    jsonattributes: jsonAttributes,
                    avoidAreas: avoidAreas,
                };
            /*for(var i=0; i < waypoints.length; i++) {
                addWaypoint(routeRequestParams, waypoints[i], i, true, i == 0 ? null : i == waypoints.length - 1 ? null : "passThrough");
            }*/
            this.currentLocation = {"lat": -33.883033, "lng": 151.200494};//-33.958497, 151.242690
            //console.log(this.currentLocation);
            //console.log("addWaypoint");
            addWaypoint(routeRequestParams, this.currentLocation, 0, true, "stopOver");
            addDestination(routeRequestParams, destination);

            //console.log("avoidAreas : " + avoidAreas);
            //addAvoidAreas(routeRequestParams, avoidAreas);

            router.calculateRoute(
                routeRequestParams,
                onSuccess,
                onError
            );
        }

        H.Map.prototype.addGeoShape = function(object) {
            this.addObject(object);
            this.bounds.push(object.getBounds());
            this.fitToBounds();
        }

        H.Map.prototype.bounds = [];

        H.Map.prototype.fitToBounds = function() {
            if (this.bounds.length != 0) {
                this.setViewBounds(H.geo.Rect.coverRects(this.bounds));
            }
        }

        /**
         * Creates a H.map.Polyline from the shape of the route and adds it to the map.
         * @param {Object} route A route as received from the H.service.RoutingService
         * @int lineWidth The width of the drawn line in pts
         * @string color Representation of the color for the drawn line
         */
        H.Map.prototype.addRouteShape = function(route, lineWidth, color) {
            var strip = new H.geo.Strip(), routeShape = route.shape, polyline;

            for(var i = 0 ; i < routeShape.length ; i++) {
                var parts = routeShape[i].split(',');
                strip.pushLatLngAlt(parts[0], parts[1]);
            }

            //console.log("addRouteShape : " + strip);
            polyline = new H.map.Polyline(strip, {
                style: {
                  lineWidth: lineWidth,
                  strokeColor: color
                }
            });
            // Add the polyline to the map
            this.addGeoShape(polyline);
        }

        H.Map.prototype.addRoute = function(platform, safeZone, areaToAvoid, lineWidth = 2, lineColor="#000", mode='fastest;car', representation='display', routeAttributes='waypoints,summary,shape,legs', maneuverAttributes='direction,action', alternatives = 0, jsonAttributes = 9) {
            //console.log(waypoints);
            let map = this;
            //console.log("avoidAreas");
            //console.log(areaToAvoid);
            platform.calculateRoute(mode, representation, routeAttributes, maneuverAttributes, safeZone, function(response) {response.response ? map.addRouteShape(response.response.route[0], lineWidth, lineColor) : null;}, error, areaToAvoid, alternatives, jsonAttributes);
        }

        H.Map.prototype.addRouteWithToAvoidAreas = function(platform, waypoints=[], avoidAreas=[], lineWidth = 2, lineColor="#000", mode='fastest;car', representation='display', routeAttributes='waypoints,summary,shape,legs', maneuverAttributes='direction,action', alternatives = 0, jsonAttributes = 9) {
            //console.log(waypoints);
            let map = this;

            avoidAreas.forEach(area => map.addPolygon(area.getBoundingPoints()));
            platform.calculateRoute(mode, representation, routeAttributes, maneuverAttributes, waypoints, function(response) {/*console.log(response);*/map.addRouteShape(response.response.route[0], lineWidth, lineColor);}, error, avoidAreas, alternatives, jsonAttributes);
        }

        H.Map.prototype.addPolygon = function(points, color="#FFFFFF88", lineWidth=2, borderColor="#000000") {
            var geoStrip = new H.geo.Strip();
            //console.log(points);
            points.forEach(x => geoStrip.pushPoint(x));
            this.addGeoShape(
                new H.map.Polygon(geoStrip, {
                    style: {
                        fillColor: color,
                        strokeColor: borderColor,
                        lineWidth: lineWidth
                    }
                })
            );
        }

        H.Map.prototype.addPolygonFromList = function(points, color="#FFFFFF88", lineWidth=0, borderColor="#000000") {
            //console.log("begin addPolygonFromList");
            var geoStrip = new H.geo.Strip();
            //console.log(points);
            var i = 0;
            while(i < points.length) {
                geoStrip.pushPoint(new H.geo.Point(points[i], points[i+1]));
                i += 2;
            }
            //console.log(geoStrip);
            this.addGeoShape(
                new H.map.Polygon(geoStrip, {
                    style: {
                        fillColor: color,
                        strokeColor: borderColor,
                        lineWidth: lineWidth
                    }
                })
            );
        }

        H.Map.prototype.addSimpleMarker = function(coords, imageLocation) {
            var icon = new H.map.Icon(imageLocation);
            var marker = new H.map.Marker(coords, {icon: icon});
            this.addObject(marker);
        }

        H.Map.prototype.addMarker = function(point, popUpContent) {
            console.log(popUpContent);
            var icon = new H.map.DomIcon(popUpContent);
            var marker = new H.map.DomMarker(point, {icon: icon});
            this.addObject(marker);
        }

        H.Map.prototype.addGoogleMarker = function(point, content, app) {
            this.addMarker(point,
                '<div style="position: initial;"><div style="display: inline-block; min-width: 100px; position: absolute; transform: translate(-50%, -100%) translate(0px, -30px); overflow: auto; max-height: 337px; max-width: 500px;background-color: white;border-radius: 5px;box-shadow: 0px 1px 6px rgba(0, 0, 0, 0.6);"><ol style="padding: 5px;margin: auto; border-radius: 5px;"><div>' + content + '</div></ol></div><div style="position: absolute; overflow: hidden; width: 16px; height: 30px;transform: translate(-60%, -100%);"><div style="position: absolute; background-color: rgb(255, 255, 255); transform: skewX(22.6deg); transform-origin: 0px 0px 0px; height: 24px; width: 10px; box-shadow: 0px 1px 0px inherit 6px rgba(0, 0, 0, 0.6);z-index: 1;"></div></div><div style="position: absolute; overflow: hidden; width: 16px; height: 30px;z-index: 1;transform: translate(5%, -100%);"><div style="background-color: rgb(255, 255, 255); transform: skewX(-22.6deg); transform-origin: 10px 0px 0px; height: 24px; width: 10px;"></div></div></div>');
            app.placeMarkers();
        }

        /* websocket communication */
        this.ws = new $WebSocket("ws://" + this.pathForWebSockets);
        this.ws.getDataStream().subscribe(
            res => {},
            function(x){
                return function(e) {
                        console.log('connection error: ' + e.message);
                        x.connect();}
                    }(this.ws),
            function(x){
                return function() {
                    console.log('connection completed');
                    x.connect();}
                }(this.ws)
        );
        this.ws.onMessage((msg: MessageEvent)=> {
                console.log("onMessage ", msg.data);
                //define what to do with that
                this.handleServerMessages(msg.data);
            },
            {autoApply: false}
        );

        this.backgroundMode.enable();

        this.geolocation.getCurrentPosition().then((resp) => {
                console.log(resp.coords.latitude + ":" + resp.coords.longitude);
                this.sendMessage(resp.coords.latitude + ":" + resp.coords.longitude);
            }).catch((error) => {
              console.log('Error getting location', error);
          });

        this.canMove = navParams.data.canMove;

        let watch = this.geolocation.watchPosition();
        watch.subscribe((data) => {
            //console.log(data);
            if(data.coords && data.coords != this.currentLocation) {
                this.currentLocation = data.coords;
                var message = {"command":"geo", "data": {"lat": data.coords.latitude, "lng": data.coords.longitude}};
                this.sendMessage(JSON.stringify(message));
            }
            else {
                console.log("error checking geolocation");
                console.log(data);
                //this.sendMessage(data);
            }
        });
    }

    error(error) {
        alert('Ooops!');
    }

    ngAfterContentInit() : void {
        this.mapContainer = this.elRef.nativeElement.querySelector('#map');
        //console.log("Begin initiate map");

        //initialize communication with the platform
        this.platform = new H.service.Platform({
          app_id: 'KZGT4fDT78t60UUHy70u',
          app_code: 'u86B6XV-EvRuxsroXzYTJw',
          useCIT: true,
          useHTTPS: true
        });
        this.defaultLayers = this.platform.createDefaultLayers();
        //this.displayMap();
    }

    returnAvoidAreaFromList(input: String, area) : String {
        //console.log("begin returnAvoidAreaFromList");
        input += area[0] + ',' + area[1] + ';' + area[2] + ',' + area[3] + "!";
        //console.log(input);
        //console.log("end returnAvoidAreaFromList");
        return input;
    };

    returnAvoidAreasFromList(areas, threshold) {
        //console.log("begin returnAvoidAreasFromList");
        //console.log(areas);
        let output: String;
        output = "";
        if(areas.length != 0) {
            for(var i = 0 ; i < areas.length ; i++) {
                //console.log(areas[i]);
                if(areas[i].risk >= threshold) {
                    output = this.returnAvoidAreaFromList(output, areas[i].boundary);
                }
            }
            output = output.substring(0, output.length-1);
        }
        //console.log("end returnAvoidAreasFromList");
        //console.log(output);
        return output;
    };

    displayMap(informations, testing = true) : void {
        //initialize a map - this map is centered over Berlin
        this.map = new H.Map(this.mapContainer,
          this.defaultLayers.normal.map,{
          center: {lat:52.5160, lng:13.3779},
          zoom: 13
        });
        this.map.bounds = [];

        //make the map interactive
        // MapEvents enables the event system
        // Behavior implements default interactions for pan/zoom (also on mobile touch environments)
        this.behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(this.map));

        // Create the default UI components
        this.ui = H.ui.UI.createDefault(this.map, this.defaultLayers);

        //console.log("End initiate map");

        var colors = ['#FFDE00', '#FF7C00', '#ED1603'];

        //for each possible destination, for each different risk-level, draw a route
        var areasToAvoid: String;
        areasToAvoid = "";
        if(testing) {
            informations.areaToAvoid = [];
            informations.displayPoly = [];
            for(let i = 0; i < 3; i++) {
                var list = [(-33.87 + Math.random()* 0.05 / (i+1)), (151 - Math.random() * 0.01 / (i+1)), (-33.87 - Math.random() * 0.01 / (i+1)), (151 + Math.random() * 0.01 / (i+1))];
                informations.areaToAvoid.push({"boundary": list, "risk": i});
                informations.displayPoly.push({"points": [list[0], list[1], list[0], list[3], list[2], list[3], list[2], list[1]], "risk": i});
            }
            informations.safeZones = [{"radius": 200, "point": [-33.5, 150.5]}];
        }
        //console.log(informations);
        for(var i = 0; i < 3; i++) {
            areasToAvoid = this.returnAvoidAreasFromList(informations.areaToAvoid, i);
            informations.safeZones.map((safeZone) => {
                this.map.addRoute(this.platform, safeZone, areasToAvoid, 4, colors[i] + "66");
            });
        }

        informations.displayPoly.map((polygon) => {
            console.log(polygon);
            this.map.addPolygonFromList(polygon.points, colors[polygon.risk] + "BB");
        });

        informations.safeZones.forEach((safeZone, index)=>{
            this.map.addGoogleMarker(new H.geo.Point(safeZone.point[0], safeZone.point[1]),
                '<span>Hi, here is a safe zone =)</span>', this);
            //this.map.addSimpleMarker({"lat": safeZone.point[0], "lng": safeZone.point[1]}, "http://25.media.tumblr.com/d9e668fac828170fd3043f063f3fc4c4/tumblr_mm9n3sdycy1ry1y7qo5_500.gif");
            this.map.addMarker({"lat": safeZone.point[0], "lng": safeZone.point[1]}, "<span>coucou</span>");
            this.map.addObject(new H.map.Marker({"lat": safeZone.point[0], "lng": safeZone.point[1]}));
        });

        var liste = [
            -33.6951609555 , 150.495160956,
            -33.6951609555 , 150.504839044,
            -33.7120976112 , 150.545970922,
            -33.7241952223 , 150.553229489,
            -33.7338733112 , 150.553229489,
            -33.7483904446 , 150.548390445,
            -33.7532294891 , 150.533873311,
            -33.7532294891 , 150.524195222,
            -33.7459709224 , 150.512097611,
            -33.7048390445 , 150.495160956,
            -33.6951609555 , 150.495160956];
        this.map.addPolygonFromList(liste, colors[2] + "BB");
        this.map.addPolygonFromList([-33.6951609555, 150.553229489, -33.6951609555 ,150.495160956, -33.7532294891, 150.495160956,-33.7532294891, 150.553229489], "#00000000", 2, "#000");

        this.map.fitToBounds();
        //this.map.setCenter({"lat":-33.6527334665 , "lng": 150.530349492});
    }

    handleServerMessages(messageContent) : void {
        console.log("handling server messages");
        var response = JSON.parse(messageContent);
        if(messageContent.type == "alert") {
            switch(response.data.dangerLevel) {
                case "hold":
                    this.danger = true;
                    this.run = false;
                    break;
                case "escape":
                    this.danger = true;
                    this.run = true;
                    break;
                default:
                    this.danger = false;
                    this.run = false;
            }
            if (this.danger && this.run) {
                setTimeout(() => {this.displayMap(response.data);}, 1);
            }
        }
    }

    getAvailableHeight() {
        //console.log("getAvailableHeigth: " + window.screen.height);
        //console.log((window.screen.height - 56 - 2*36) + "px");
        return (window.screen.height - 56 - 2*36) + "px";
    }

    /*alertRescueTeam() : void {
        var message = {};
        this.sendMessage("{'type': }request for help");
    }*/

    turnDangerOnOff() : void {
        this.danger = !this.danger;
        //while(this.mapContainer.offsetHeight < 100) {
         setTimeout(() => {console.log(this.mapContainer.offsetHeight); this.displayMap({}, true);}, 1);
        //}
    }

    turnRunOnOff() : void {
        this.run = !this.run;
        //while(this.mapContainer.offsetHeight < 100) {
         setTimeout(() => {console.log(this.mapContainer.offsetHeight); this.displayMap({}, true);}, 1);
        //}
    }

    /*reportFire() : void {
        this.sendMessage("report fire");
    }*/
}
