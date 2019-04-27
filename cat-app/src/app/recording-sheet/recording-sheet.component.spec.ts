import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RecordingSheetComponent } from './recording-sheet.component';

describe('RecordingSheetComponent', () => {
  let component: RecordingSheetComponent;
  let fixture: ComponentFixture<RecordingSheetComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RecordingSheetComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RecordingSheetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
