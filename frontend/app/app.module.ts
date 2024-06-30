import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { HeaderComponent } from './header/header.component';
import { AnalyseEmbryonComponent } from './analyse-embryon/analyse-embryon.component';
import { HttpClientModule } from '@angular/common/http';
import { ToastrModule } from 'ngx-toastr';
import { LoginComponent } from './login/login.component';
import { ListComponent } from './list/list.component';
import { MaterialModule } from './material.module';
import { NgCircleProgressModule } from 'ng-circle-progress';

// import { ButtonModule } from 'primeng/button';
// import { CardModule } from 'primeng/card';
// import { FileUploadModule } from 'primeng/fileupload';
// import { InputTextModule } from 'primeng/inputtext';
// import { ToastModule } from 'primeng/toast';
// import { ToolbarModule } from 'primeng/toolbar';
// import { MessagesModule } from 'primeng/messages';
// import { MessageModule } from 'primeng/message';
@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    HeaderComponent,
    AnalyseEmbryonComponent,
    LoginComponent,
    ListComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    NgCircleProgressModule.forRoot({
      // set defaults here
      radius: 60,
      outerStrokeWidth: 10,
      innerStrokeWidth: 5,
      outerStrokeColor: "#78C000",
      innerStrokeColor: "#C7E596",
      animationDuration: 300,
    }),
    //MaterialModule,
    FormsModule, // Add FormsModule here
    HttpClientModule, //backend
    ToastrModule.forRoot({
      positionClass: 'toast-top-right',
      preventDuplicates: true,
      progressBar: true,
      timeOut: 3000,
      closeButton: true,
    }),
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
