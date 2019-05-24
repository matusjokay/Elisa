import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CollisionDetailComponent } from './collision-detail.component';

describe('CollisionDetailComponent', () => {
  let component: CollisionDetailComponent;
  let fixture: ComponentFixture<CollisionDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CollisionDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CollisionDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
