import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TimetableUpdateMainComponent } from './timetable-update-main.component';

describe('TimetableUpdateMainComponent', () => {
  let component: TimetableUpdateMainComponent;
  let fixture: ComponentFixture<TimetableUpdateMainComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TimetableUpdateMainComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TimetableUpdateMainComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
