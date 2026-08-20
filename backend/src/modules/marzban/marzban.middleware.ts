import { Request, Response, NextFunction } from 'express';

import { Injectable, NestMiddleware } from '@nestjs/common';

import { MarzbanService } from './marzban.service';

@Injectable()
export class MarzbanMiddleware implements NestMiddleware {
    constructor(private readonly marzbanService: MarzbanService) {}
    async use(
        req: { clientIp: string; resolvedShortUuid?: string | null } & Request,
        res: Response,
        next: NextFunction,
    ) {
        const marzbanShortUuidParam = req.params.shortUuid;
        const marzbanShortUuid = Array.isArray(marzbanShortUuidParam)
            ? marzbanShortUuidParam[0]
            : marzbanShortUuidParam;

        const resolvedShortUuid = await this.marzbanService.resolveShortUuid(
            marzbanShortUuid,
            req.clientIp,
        );

        if (resolvedShortUuid.dropConnection) {
            res.socket?.destroy();
            return;
        }

        if (resolvedShortUuid.shortUuid) {
            req.resolvedShortUuid = resolvedShortUuid.shortUuid;
        }

        next();
    }
}
