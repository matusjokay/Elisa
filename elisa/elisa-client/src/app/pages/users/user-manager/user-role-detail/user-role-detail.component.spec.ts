import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UserRoleDetailComponent } from './user-role-detail.component';

describe('UserRoleDetailComponent', () => {
  let component: UserRoleDetailComponent;
  let fixture: ComponentFixture<UserRoleDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ UserRoleDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UserRoleDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
