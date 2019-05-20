import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TimetableUpdateFormComponent } from './timetable-update-form.component';

describe('TimetableUpdateFormComponent', () => {
  let component: TimetableUpdateFormComponent;
  let fixture: ComponentFixture<TimetableUpdateFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TimetableUpdateFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TimetableUpdateFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
