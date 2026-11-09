import { Component } from '@angular/core';

@Component({
  selector: 'app-businesses',
  imports: [],
  templateUrl: './businesses.html',
  styleUrl: './businesses.css',
})
export class Businesses {
  business_list = [
    { name: 'Pizza Mountain', town: 'Coleraine', rating: 5 },
    { name: 'Wine Lake', town: 'Ballymoney', rating: 3 },
    { name: 'Sweet Desert', town: 'Ballymena', rating: 4 },
  ];
} 