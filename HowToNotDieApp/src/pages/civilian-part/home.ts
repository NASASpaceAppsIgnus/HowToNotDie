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



    constructor(public navCtrl: NavController, private elRef: ElementRef, private backgroundMode: BackgroundMode, private geolocation: Geolocation, public navParams: NavParams) {
        console.log("arrived on civilian-part");


    }

    
}
