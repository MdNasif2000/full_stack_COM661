import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Businesses } from './components/businesses/businesses';
// import jsonData from '../data/data.json';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Businesses],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected title = 'BizFE';
  ngOnInit() {
    // console.log(jsonData);
  }
}
