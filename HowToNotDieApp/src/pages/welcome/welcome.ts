import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';
import { CivilianPartPage } from '../civilian-part/home';

@Component({
  selector: 'page-hello-ionic',
  templateUrl: 'hello-ionic.html'
})
export class WelcomePage {
    public danger:boolean = false;

    constructor(public navCtrl: NavController) {

    }

    openCivilianPart(event, canMove: boolean) {
        console.log("going to civilian-part");
        this.navCtrl.push(CivilianPartPage, {"canMove": canMove});
    }
}
