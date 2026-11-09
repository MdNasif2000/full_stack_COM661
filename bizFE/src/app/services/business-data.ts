import { Injectable } from '@angular/core';
import jsonData from '../../data/data.json'
@Injectable({
  providedIn: 'root',
})
export class BusinessData {
  pageSize: number = 3;
  getBusiness(page: number) {
    let pageStart = (page - 1) * this.pageSize;
    let pageEnd = pageStart + this.pageSize;
    return jsonData.slice(pageStart, pageEnd);
  }
  getLastPageNumber() {
    return Math.ceil(jsonData.length / this.pageSize);
  }
}
