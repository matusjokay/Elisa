import { Component, OnInit } from '@angular/core';
import {TimetableService} from '../../../services/timetable.service';
import {zip} from 'rxjs';

@Component({
  selector: 'app-version-list',
  templateUrl: './version-list.component.html',
  styleUrls: ['./version-list.component.less']
})
export class VersionListComponent implements OnInit {
  schemas: any;

  constructor(
    private timetableService: TimetableService,
  ) { }

  ngOnInit() {
    zip(
      this.timetableService.getAllSchemas(),
      this.timetableService.getTimetableVersions(1)
      ).subscribe(([schemasData,versionsData])=>{
        // this.schemas = schemasData;

    });
  }

}
