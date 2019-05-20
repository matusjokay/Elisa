import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TimetableUpdateWrapperComponent } from './timetable-update-wrapper.component';

describe('TimetableUpdateWrapperComponent', () => {
  let component: TimetableUpdateWrapperComponent;
  let fixture: ComponentFixture<TimetableUpdateWrapperComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TimetableUpdateWrapperComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TimetableUpdateWrapperComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
