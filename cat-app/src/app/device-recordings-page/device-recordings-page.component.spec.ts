import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DeviceRecordingsPageComponent } from './device-recordings-page.component';

describe('DeviceRecordingsPageComponent', () => {
  let component: DeviceRecordingsPageComponent;
  let fixture: ComponentFixture<DeviceRecordingsPageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DeviceRecordingsPageComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DeviceRecordingsPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
