import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DepartmentUserDetailComponent } from './department-user-detail.component';

describe('DepartmentUserDetailComponent', () => {
  let component: DepartmentUserDetailComponent;
  let fixture: ComponentFixture<DepartmentUserDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DepartmentUserDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DepartmentUserDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
