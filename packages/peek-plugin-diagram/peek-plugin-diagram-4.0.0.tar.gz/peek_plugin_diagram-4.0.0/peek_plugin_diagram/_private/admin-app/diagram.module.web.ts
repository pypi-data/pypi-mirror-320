import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Route, Routes } from "@angular/router";
import { EditSettingComponent } from "./components/edit-setting-table/edit.component";
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleDataOfflineObserverService,
} from "@synerty/vortexjs";
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzGridModule } from "ng-zorro-antd/grid";
import { NzBadgeModule } from "ng-zorro-antd/badge";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzTagModule } from "ng-zorro-antd/tag";

// Import our components
import { DiagramPageComponent } from "./components/diagram-page/diagram-page.component";
import { StatusComponent } from "./components/status/status.component";
import {
    diagramActionProcessorName,
    diagramFilt,
    diagramObservableName,
    diagramTupleOfflineServiceName,
} from "@peek/peek_plugin_diagram/_private";
import { NzDescriptionsModule } from "ng-zorro-antd/descriptions";

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        diagramActionProcessorName,
        diagramFilt,
    );
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(
        diagramObservableName,
        diagramFilt,
    );
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(diagramTupleOfflineServiceName);
}

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: DiagramPageComponent,
    },
];

// Define the module
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        ReactiveFormsModule,
        NzTabsModule,
        NzTableModule,
        NzButtonModule,
        NzInputModule,
        NzCardModule,
        NzSwitchModule,
        NzFormModule,
        NzGridModule,
        NzBadgeModule,
        NzInputNumberModule,
        NzDividerModule,
        NzTagModule,
        NzDescriptionsModule,
    ],
    exports: [],
    providers: [
        TupleActionPushService,
        {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory,
        },
        TupleOfflineStorageService,
        {
            provide: TupleOfflineStorageNameService,
            useFactory: tupleOfflineStorageNameServiceFactory,
        },
        TupleDataObserverService,
        TupleDataOfflineObserverService,
        {
            provide: TupleDataObservableNameService,
            useFactory: tupleDataObservableNameServiceFactory,
        },
    ],
    declarations: [DiagramPageComponent, StatusComponent, EditSettingComponent],
})
export class PeekPluginDiagramModule {}
