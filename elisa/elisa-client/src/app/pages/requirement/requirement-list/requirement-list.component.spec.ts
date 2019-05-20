import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequirementListComponent } from './requirement-list.component';

describe('RequirementListComponent', () => {
  let component: RequirementListComponent;
  let fixture: ComponentFixture<RequirementListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequirementListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequirementListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
