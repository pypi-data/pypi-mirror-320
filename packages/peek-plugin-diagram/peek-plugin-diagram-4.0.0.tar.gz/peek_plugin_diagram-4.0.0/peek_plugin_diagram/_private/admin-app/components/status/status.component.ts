import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { DiagramImporterStatusTuple } from "../../tuples/DiagramImporterStatusTuple";

interface StatusTableData {
    name: string;
    isRunning: boolean;
    queueSize: number;
    totalProcessed: number;
    lastError: string;
}

@Component({
    selector: "pl-diagram-status",
    templateUrl: "./status.component.html",
    styleUrls: ["./status.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class StatusComponent extends NgLifeCycleEvents {
    protected readonly status$ = new BehaviorSubject<StatusTableData[]>([]);
    protected readonly loading$ = new BehaviorSubject<boolean>(true);

    protected readonly columns = [
        { title: "Name", key: "name", width: "150px" },
        { title: "Is Running", key: "isRunning", width: "100px" },
        { title: "Queue Size", key: "queueSize", width: "100px" },
        { title: "Total Processed", key: "totalProcessed", width: "120px" },
        { title: "Last Error", key: "lastError" },
    ];

    constructor(
        private balloonMsg: BalloonMsgService,
        private tupleObserver: TupleDataObserverService,
    ) {
        super();

        let ts = new TupleSelector(DiagramImporterStatusTuple.tupleName, {});
        this.tupleObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuple = <DiagramImporterStatusTuple[]>tuples;
                if (!tuples.length) {
                    this.status$.next([]);
                    return;
                }

                const item = typedTuple[0];
                this.status$.next([
                    {
                        name: "Display Compiler",
                        isRunning: item.displayCompilerQueueStatus,
                        queueSize: item.displayCompilerQueueSize,
                        totalProcessed: item.displayCompilerProcessedTotal,
                        lastError: item.displayCompilerLastError,
                    },
                    {
                        name: "Grid Compiler",
                        isRunning: item.gridCompilerQueueStatus,
                        queueSize: item.gridCompilerQueueSize,
                        totalProcessed: item.gridCompilerProcessedTotal,
                        lastError: item.gridCompilerLastError,
                    },
                    {
                        name: "Location Compiler",
                        isRunning: item.locationIndexCompilerQueueStatus,
                        queueSize: item.locationIndexCompilerQueueSize,
                        totalProcessed:
                            item.locationIndexCompilerProcessedTotal,
                        lastError: item.locationIndexCompilerLastError,
                    },
                    {
                        name: "Branch Compiler",
                        isRunning: item.branchIndexCompilerQueueStatus,
                        queueSize: item.branchIndexCompilerQueueSize,
                        totalProcessed: item.branchIndexCompilerProcessedTotal,
                        lastError: item.branchIndexCompilerLastError,
                    },
                ]);
                this.loading$.next(false);
            });
    }
}
