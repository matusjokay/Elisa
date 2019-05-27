import { Component, OnInit } from '@angular/core';
import {TimetableService} from '../../../services/timetable.service';
import {FormControl, FormGroup} from '@angular/forms';

@Component({
  selector: 'app-timetable-new',
  templateUrl: './timetable-new.component.html',
  styleUrls: ['./timetable-new.component.less']
})
export class TimetableNewComponent implements OnInit {

  schemas: any;
  schemaForm: FormGroup;
  constructor(
    private timetableService: TimetableService,
  ) { }

  ngOnInit() {
    this.timetableService.getAllSchemas().subscribe(
      (response: any) =>{
        this.schemas = response;
      }
    );

    this.schemaForm = new FormGroup({
      'name': new FormControl(),
      'parent_schema': new FormControl(),
    });
  }

  onSubmit(){
    let post = this.schemaForm.value;
    if(post['parent_schema'] === null){
      delete post['parent_schema'];
    }
    post['is_active'] = true;
    this.timetableService.createSchema(post).subscribe(response =>{
      this.createDefaultVersion();
    });
  }

  createDefaultVersion(){
    let defaultVersion = {
      name: "Nový rozvrh",
    };
    this.timetableService.createVersion(defaultVersion).subscribe();
  }
}
