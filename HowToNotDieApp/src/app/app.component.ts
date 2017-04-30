import { Component, ViewChild } from '@angular/core';

import { Platform, MenuController, Nav } from 'ionic-angular';

import { WelcomePage } from '../pages/welcome/welcome';
import { ItemDetailsPage } from '../pages/item-details/item-details';

import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';

import { LocalNotifications } from '@ionic-native/local-notifications';

@Component({
  templateUrl: 'app.html'
})
export class MyApp {
  @ViewChild(Nav) nav: Nav;

  // make HelloIonicPage the root (or first) page
  rootPage = WelcomePage;
  pages : any = [];

  constructor(
    public platform: Platform,
    public menu: MenuController,
    public statusBar: StatusBar,
    public splashScreen: SplashScreen,
    public localNotifications: LocalNotifications
  ) {
    this.initializeApp();

    this.pages.push({"title": "Home", "component": WelcomePage});
    this.pages.push({"title": "Kitten", "image": "http://25.media.tumblr.com/d9e668fac828170fd3043f063f3fc4c4/tumblr_mm9n3sdycy1ry1y7qo5_500.gif", "text": "This is a normal kitten", "component": ItemDetailsPage});
    this.pages.push({"title": "Evil kitten", "image": "http://img.memecdn.com/evil-cat_o_762275.gif", "text": "This is an evil kitten", "component": ItemDetailsPage});
    console.log(this.pages);
  }

  initializeApp() {
    this.platform.ready().then(() => {
      // Okay, so the platform is ready and our plugins are available.
      // Here you can do any higher level native things you might need.
      this.statusBar.styleDefault();
      this.splashScreen.hide();
    });
  }

  openPage(page) {
      console.log("clicked on " + page);
      this.nav.push(page.component, {
        item: page
      });
      this.menu.close();
  }
}
