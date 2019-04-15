import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DeviceSettingsEditComponent } from './device-settings-edit.component';

describe('DeviceSettingsEditComponent', () => {
  let component: DeviceSettingsEditComponent;
  let fixture: ComponentFixture<DeviceSettingsEditComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DeviceSettingsEditComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DeviceSettingsEditComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
