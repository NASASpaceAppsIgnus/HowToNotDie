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
    this.pages.push({"title": "What should you do ?", "component": ItemDetailsPage, "text": "<h1>Leave early or prepare to stay ?</h1><p>One of the most important things to do before a bush fire is to decide what you’ll do if one should start. This guide can help you make that decision, and assist you with the steps in preparing yourself, your home and your family. Once you’ve had the discussion and made a decision, get your family to sign this document"});
    this.pages.push({"title": "Leaving", "component": ItemDetailsPage, "text": "<h1>Leaving early is your safest choice</h1><h2>...but you still need to prepare it.</h2><ul><li>When will we leave?</li><li>What will be your sign to leave? </li><li>Where will we go?</li><li>Where’s a meeting place that’s safe and away from a fire area? </li><li>What will we take?</li><li>Who will we call to tell that we’re leaving and that we have arrived safely?</li><li>Who will we call to let them know we’re leaving and that we’ve got there safely?</li><li>What is our backup plan?</li><li>What if things don’t go to plan?</li></ul>"});
    this.pages.push({"title": "When to leave?", "text":"What will be your sign to leave? It could be smoke in your area, or as soon as you find out there’s a fire near you.", "component": ItemDetailsPage});
    this.pages.push({"title": "Where will we go?", "text": "Where’s a meeting place that’s safe and away from a fire area? It might be a friend or relative’s place, or even a shopping centre.", "component": ItemDetailsPage});
    this.pages.push({"title": "Staying", "text": "<h1>ONLY IF YOU’RE WELL PREPARED</h1><div>Before you start, ask your household: <ul><li>Is your home well prepared to make it as safe as possible during a fire? <br />Check the Step 2 property protection checklists. </li><li>Are we putting anyone in our family at risk by staying?</br />For example children, the elderly, or people with asthma.</li><li>Will we cope in an emergency situation? In a fire, it will be hot, smoky and physically draining. Even trained firefighters can find it challenging.</li></ul>If you’re not sure or aren’t prepared, you should leave early.</div>", "component":ItemDetailsPage});
    this.pages.push({"title": "Kitten", "image": "http://25.media.tumblr.com/d9e668fac828170fd3043f063f3fc4c4/tumblr_mm9n3sdycy1ry1y7qo5_500.gif", "text": "This is a normal kitten", "component": ItemDetailsPage});
    this.pages.push({"title": "Evil kitten", "image": "http://img.memecdn.com/evil-cat_o_762275.gif", "text": "This is an evil kitten", "component": ItemDetailsPage});
    console.log(this.pages);

    /*while(!this.localNotifications.hasPermission()) {
        if (!this.localNotifications.registerPermission()) {
            alert("We need to be able to warn from near fires !");
        }
    }*/
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
