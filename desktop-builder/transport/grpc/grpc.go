package grpc

import (
	"context"
	"fmt"
	"net"

	"github.com/isard-vdi/isard/desktop-builder/desktopbuilder"
	"github.com/isard-vdi/isard/desktop-builder/env"
	"github.com/isard-vdi/isard/desktop-builder/pkg/proto"

	gRPC "google.golang.org/grpc"
)

// API is the version for the gRPC API
const API = "v1.0.0"

// DesktopBuilderServer implements the gRPC server
type DesktopBuilderServer struct {
	env     *env.Env
	builder desktopbuilder.Interface
}

// Serve starts the DesktopBuilder gRPC server
func Serve(ctx context.Context, env *env.Env, builder desktopbuilder.Interface) {
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", env.Cfg.GRPC.Port))
	if err != nil {
		env.Sugar.Fatalw("listen gRPC port",
			"err", err,
			"port", env.Cfg.GRPC.Port,
		)
	}

	srv := &DesktopBuilderServer{env, builder}
	s := gRPC.NewServer()
	proto.RegisterDesktopBuilderServer(s, srv)

	env.Sugar.Infow("desktop builder gRPC serving",
		"port", env.Cfg.GRPC.Port,
	)
	go func() {
		if err = s.Serve(lis); err != nil {
			if err != gRPC.ErrServerStopped {
				env.Sugar.Fatalw("serve desktop builder gRPC",
					"err", err,
					"port", env.Cfg.GRPC.Port,
				)
			}
		}
	}()

	select {
	case <-ctx.Done():
		s.Stop()
		env.WG.Done()
	}
}
