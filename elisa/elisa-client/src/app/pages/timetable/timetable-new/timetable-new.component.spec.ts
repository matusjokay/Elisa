import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TimetableNewComponent } from './timetable-new.component';

describe('TimetableNewComponent', () => {
  let component: TimetableNewComponent;
  let fixture: ComponentFixture<TimetableNewComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TimetableNewComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TimetableNewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
