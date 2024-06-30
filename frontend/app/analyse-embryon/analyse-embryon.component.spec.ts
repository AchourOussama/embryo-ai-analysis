import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AnalyseEmbryonComponent } from './analyse-embryon.component';

describe('AnalyseEmbryonComponent', () => {
  let component: AnalyseEmbryonComponent;
  let fixture: ComponentFixture<AnalyseEmbryonComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [AnalyseEmbryonComponent]
    });
    fixture = TestBed.createComponent(AnalyseEmbryonComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
