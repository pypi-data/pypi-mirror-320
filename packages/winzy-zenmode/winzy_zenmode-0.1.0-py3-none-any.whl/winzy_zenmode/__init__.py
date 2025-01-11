import winzy
from winzy_zenmode.ontop import keep_window_on_top


def create_parser(subparser):
    parser = subparser.add_parser(
        "zenmode",
        description="Zenmode stay focussed with only the priority windows and nothing else.",
    )
    # Add subprser arguments here.
    parser.add_argument(
        "-d",
        "--duration",
        type=str,
        default="1m",
        help="Duration to keep the window on top 1m, 30s, 1h ",
    )
    return parser


class WinzyPlugin:
    """ Zenmode stay focussed with only the priority windows and nothing else. """

    __name__ = "zenmode"

    @winzy.hookimpl
    def register_commands(self, subparser):
        self.parser = create_parser(subparser)
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        try:
            keep_window_on_top(duration=args.duration)
        except ValueError as e:
            print(str(e))

    def hello(self, args):
        # this routine will be called when 'winzy zenmode' is called.
        print("Hello! This is an example ``winzy`` plugin.")


zenmode_plugin = WinzyPlugin()
