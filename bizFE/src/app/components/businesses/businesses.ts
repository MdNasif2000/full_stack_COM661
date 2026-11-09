import { Component } from '@angular/core';
import { BusinessData } from '../../services/business-data';

@Component({
  selector: 'app-businesses',
  imports: [],
  providers :[BusinessData],
  templateUrl: './businesses.html',
  styleUrl: './businesses.css',
})
export class Businesses {
  business_list: any[] = [];
  page: number = 1;
  constructor(protected businessData: BusinessData) { }
  ngOnInit(){
    this.business_list = this.businessData.getBusiness(this.page);
  }
  
  nextPage() {
    if (this.page < this.businessData.getLastPageNumber()) {
      this.page = this.page + 1;
      this.business_list = this.businessData.getBusiness(this.page);
    }

  }
  previousPage() {
    if (this.page > 1) {
      this.page = this.page - 1
      this.business_list = this.businessData.getBusiness(this.page);
    }
  }

  // business_list = [
  //   { name: 'Pizza Mountain', town: 'Coleraine', rating: 5 },
  //   { name: 'Wine Lake', town: 'Ballymoney', rating: 3 },
  //   { name: 'Sweet Desert', town: 'Ballymena', rating: 4 },
  // ];
} 