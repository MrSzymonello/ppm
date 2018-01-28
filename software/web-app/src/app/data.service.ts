import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import 'rxjs/add/operator/map';

@Injectable()
export class DataService {

  constructor(private http: Http) { }

  latestPpmData() {
    return this.http.get("http://localhost:5000/api/ppm/");
  }

}
