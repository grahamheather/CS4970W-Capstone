import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AddDeviceSheetComponent } from './add-device-sheet.component';

describe('AddDeviceSheetComponent', () => {
  let component: AddDeviceSheetComponent;
  let fixture: ComponentFixture<AddDeviceSheetComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddDeviceSheetComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddDeviceSheetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
